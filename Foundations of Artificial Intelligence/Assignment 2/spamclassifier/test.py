# ---- Stage 5: Model comparison and selection ----
# Set RUN_TESTING = True to rerun the comparison (~15 seconds). Not needed
# to build the submitted classifier.
RUN_TESTING = False

import time

def compare_models(X: np.ndarray, y: np.ndarray, k: int = 10) -> dict:
    """
    Cross-validates each candidate model on the same k folds (cross_validate()
    uses seed = 0 throughout) and prints a comparison table. Because the folds
    are identical, the per-fold accuracies are paired so two models can be
    compared fold by fold rather than only by their means (Dietterich, 1998).

    The model with the highest CV mean is selected, unless a simpler model is
    within one standard error (std / sqrt(k)) of it, in which case the simpler
    model is preferred.

    Args:
        X: features, shape (n, 54)
        y: labels, 0 = ham and 1 = spam, shape (n, )

    Returns:
        dict of model name -> fold accuracies, shape (k, )
    """
    candidates = {
        "Baseline (most common class)": MostCommonClass,
        "Naive Bayes (Bernoulli, alpha=1)": NaiveBayesClassifier,
        "Logistic regression (lr=0.5, 1000 epochs, l2=0)": LogisticRegressionClassifier,
        "Feedforward NN (16 ReLU units, lr=0.5, 1000 epochs, l2=0)": FeedforwardClassifier,
    }

    results = {}
    rows = []
    for name, make_model in candidates.items():
        mean, std, per_fold = cross_validate(make_model, X, y, k=k, verbose=False)
        results[name] = per_fold

        # Train once on all emails for the training accuracy and timing.
        start = time.perf_counter()
        model = make_model()
        model.train(X, y)
        train_time = time.perf_counter() - start
        train_acc = float(np.mean(model.predict(X) == y))

        rows.append((name, mean, std, std / np.sqrt(k), train_acc, train_acc - mean, train_time))

    # Markdown table: gap = train acc - CV mean, a large gap suggests over-fitting.
    print("| Model | CV mean | CV std | Std error | Train acc | Gap | Train time (s) |")
    print("|---|---|---|---|---|---|---|")
    for name, mean, std, se, train_acc, gap, t in rows:
        print(f"| {name} | {mean:.3f} | {std:.3f} | {se:.3f} | {train_acc:.3f} | {gap:+.3f} | {t:.2f} |")

    # Rank the models by CV mean. Cross-validation has now run, so this is the
    # first point at which the two strongest models are known.
    ranked_models = sorted(rows, key=lambda row: row[1], reverse=True)
    best_model, best_mean, _, best_std_error, *_ = ranked_models[0]
    second_best_model, second_best_mean, _, second_best_std_error, *_ = ranked_models[1]
    print(f"\nTop two by CV mean: {best_model} {best_mean:.3f} ± {best_std_error:.3f} vs "
          f"{second_best_model} {second_best_mean:.3f} ± {second_best_std_error:.3f}")

    # Paired fold-by-fold comparison of the two strongest models.
    # Same folds, so each difference is a fair head-to-head on the same emails.
    diff = model_results[second_best_model] - model_results[best_model]
    print(f"\nFold-by-fold accuracy comparison: {second_best_model} minus {best_model}:")
    print("  per fold:", np.array2string(diff, precision=3))
    print(f"  mean difference = {diff.mean():+.3f}, std = {diff.std():.3f}, "
          f"std error = {diff.std() / np.sqrt(k):.3f}")
    print(f"  {second_best_model} better on {int((diff > 0).sum())} folds, "
          f"{best_model} better on {int((diff < 0).sum())} folds, "
          f"tied on {int((diff == 0).sum())} folds")

    # Apply the one-standard error method from the docstring.
    within_std_error = [row[0] for row in ranked_models[1:] if best_mean - row[1] <= best_std_error]
    print(f"\nHighest CV mean: {best_model} ({best_mean:.3f})")
    if within_std_error:
        print("Within one standard error of it:", "; ".join(within_std_error))
        print("=> The difference is not distinguishable from fold-to-fold noise, "
              "so the simpler of these models is selected.")
    else:
        print("=> No other model is within one standard error, so this model is selected.")

    return model_results

if RUN_TESTING:
    comparison_results = compare_models(X, y)
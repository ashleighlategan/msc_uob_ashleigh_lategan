def run():
    print("Hello!")
    num = ""
    total = 0

    while True:
        print("Enter an integer, or enter 'quit' to quit:")

        num = input(">>> ")
        if num == "quit":
            break

        try:
            num = int(num)
        except ValueError:
            print("Please enter a valid integer or 'quit'")
            continue

        total += num

    print(f"Your total was: {total}")

run()
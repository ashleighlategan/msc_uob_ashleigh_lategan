import math
from enigma import EnigmaMachine, Reflector, ALPHABET
from enigma_enhanced import EnhancedReflector, EnhancedEnigmaMachine

# In the original A reflector wiring E mapped to A and A mapped to E 
# and J mapped to B and B mapped to J
# In the new A wiring, J maps to A but A still maps to E, and
# E maps to B but B still maps to J
NEW_A_WIRING = "JEMZALYXVBWFCRQUONTSPIKHGD"

def enhanced_reflector_testing():
    """Checks that the behaviour of the EnhancedReflector meets expectations."""

    # Construct an instance
    
    ref = EnhancedReflector("New_A", NEW_A_WIRING)
    assert ref.name == "New_A"
    assert ref.wiring == NEW_A_WIRING

    # Encode should use the forward wiring 
    assert ref.encode("B") == NEW_A_WIRING[1]

    # Decode should use the inverse wiring such that you get the original letter back
    assert ref.decode(NEW_A_WIRING[1]) == "B"

    # Compare to the standard reflector from the EnigmaMachine that is self-inverse,
    # where encode(encode(c)) == c for any alphabetic character

    standard_ref = Reflector("A")
    for c in ALPHABET:
        assert standard_ref.encode(standard_ref.encode(c)) == c

    # The EnhancedReflector should not be self-inverse, such that
    # encode(encode(c)) would not return c

    self_inverse_true = all(ref.encode(ref.encode(c)) == c for c in ALPHABET)

    assert not self_inverse_true, ("""The EnhancedReflector is designed to not be self-inverse such that 
                                   encode and decode paths are different.""")
    
    # Even if not self-inverse, encode(decode(c)) should return the original c
    for c in ALPHABET:
        assert ref.decode(ref.encode(c)) == c, (f"Testing the decode(encode('{c}')) should return '{c}'")
    
    # Testing wiring length
    try:
        EnhancedReflector("reflector_short","JEMZAL")
        assert False, "Should have raised a ValueError for incorrect wiring length"
    except ValueError:
        pass

    # Testing wiring with non-alphabetical characters

    try:
        EnhancedReflector("reflector_short","7EMZALYXVBWFCRQUONTSPIKHGD")
        assert False, "Should have raised a ValueError for non-alphabetical characters"
    except ValueError:
        pass

    # Testing repeated letters in wiring string
    try:
        EnhancedReflector("reflector_repeat", "JEMZBLYXVBWFCRQUONTSPIKHGD")             # B is repeated and A is missing
        assert False, "Should have raised a ValueError for repeated letters"
    except ValueError:
        pass

    print("All EnhancedReflector tests have been passed.")

def enhanced_enigma_testing():
    """Checks that the behaviour of the EnhancedEnigmaMachine meets expectations and
    validating the codebreaking effects discussed by Thimbleby (2016)"""

    # Test 1: The standard enigma machine cannot have a letter encrypt to itself
    standard_machine = EnigmaMachine(
        rotor_names = ['Beta', 'I', 'II'],
        reflector = Reflector("A"),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )
    for c in ALPHABET:
        assert standard_machine.encode_character(c) != c, (f"Inputs to the standard enigma machine like '{c}' should never encode to themself.")
        
    print("Test 1 passed showing that the standard machine does not support self-coding.")

    # Test 2: Removing the non-self-coding constraint
    # The standard enigma machine cannot have a letter map to itself.
    # The EnhancedEnigma machine is setup such that it no longer has this restriction 
    # We need to check that passing wiring for the reflector where a letter maps to itself, is accepted

    self_coding_wiring = ALPHABET
    ref_self_code = EnhancedReflector("self-code reflector", self_coding_wiring)
    assert ref_self_code.encode("A") == "A",\
        ("A letter should be able to encode to itself using the EnhancedReflector with the necessary wiring provided.")
        
    print("Test 2 passed showing that the enhanced reflector does not have the non-self-coding constraint.")

    # Test 3: The EnhancedEnigmaMachine can encode a letter to itself
    # An input letter self-encodes at the machine level when the plugboard and rotors send its signal to one of the reflector fixed points
    # The reflector then returns the letter unchanged and the rotors and plugboard undo their scrambling from left to right.
    # We use a fresh machine for each letter below to ensure that the rotor starting positions remain fixed, and
    # each fixed point in the reflector is hit by exactly one of the inputs.

    self_coding_ref = "ABCDFGHIJKLMNOPQRSTUVWXYZE"                              # A, B, C and D map to themselves (fixed points)
    fixed_ref_points = [ALPHABET[i] for i, ch in enumerate(self_coding_ref) if ch == ALPHABET[i]]

    def self_encoding(c: str) -> bool:
        mach = EnhancedEnigmaMachine(['Beta', 'II', 'V'],
                                     EnhancedReflector("fixed_reflector", self_coding_ref),
                                     [1, 1, 1],
                                     "AAA"
                                     )
        return mach.encode_character(c) == c

    self_coding_letters = [c for c in ALPHABET if self_encoding(c)]
    assert len(self_coding_letters) == len(fixed_ref_points), (f"Expected to get: {len(fixed_ref_points)} machine-level self-coding letters "
                                                               f"but got: {len(self_coding_letters)} which are: {self_coding_letters}.")
    print(f"Test 3 passes: the EnhancedEnigmaMachine self-encodes {self_coding_letters}.")

    # Test 4: Removing the reciprocal coding constraint.
    # The standard enigma machine was symmetrical such that encoding and decoding were the same with the same machine settings.
    # For example inputting a character "A" encodes to "D" and at the same settings, "D" then encodes back to "A".
    # The EnhancedEnigmaMachine does not have this feature so encoding a input character and then encoding the output should not return the same input character.

    # Two separate machines are required for this test since the relevant rotor(s) advance with each keypress.
    # If the same machine was reused, it would be starting off at the wrong rotor position(s).

    enhanced_machine_1 = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector("New_A", NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )
    enhanced_machine_2 = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector("New_A", NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )

    reciprocal_constraint_present = all(enhanced_machine_2.encode_character(enhanced_machine_1.encode_character(c))
                                            == c for c in ALPHABET)
    assert not reciprocal_constraint_present, ("The EnhancedEnigmaMachine's encode is not self-inverse.")

    print("Test 4 passed: The EnhancedEnigmaMachine no longer features the reciprocal coding constraint" )

    # Test 5: Checking decode produces the original input
    # such that decode(encode(text)) == text
    # Like in test 4 we require 2 separate machines to test this, since the relevant rotor(s) will advance with each keypress. 

    encoding_machine = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector("New_A", NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        plugboard_pairs = ['AB', 'EF', 'XY'],  
        )
    
    decoding_machine = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector("New_A", NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        plugboard_pairs = ['AB', 'EF', 'XY'],  
        )
    
    input_text = "THISISTESTFOUROFTHEENHANCEDENIGMAMACHINE"
    encrypted_text = encoding_machine.encode_string(input_text)
    decrypted_text = decoding_machine.decode_string(encrypted_text)

    assert decrypted_text == input_text, (f""" Decoding the encrypted_text should return {input_text}, 
                                              result was: {decrypted_text}.""")
    
    print("Test 5 passed showing that the separate decode method works to return the input string for the same machine settings")

    # Test 6: The EnhancedEnigmaMachine reflector shouldn't work with a standard reflector

    try:
        EnhancedEnigmaMachine(
            rotor_names = ["Beta", 'II', 'V'],
            reflector = Reflector("A"),
            ring_settings = [1, 1, 1],
            starting_positions = "AAA",
            )
        assert False, "Should have raised a ValueError."
    
    except ValueError:
        pass
    
    print("Test 6 passed showing that the EnhancedEnigmaMachine will not work with a standard reflector.") 

    # Test 7: decode_character and decode_string testing
    # Like encode_character requires alphabetical letters

    try: 
        decoding_machine.decode_character("7")
        assert False, "Should have raised a ValueError for a non-alphabetical character."
    except ValueError:
        pass

    print("Test 7 passed showing that decode_character will not accept non-alphabetical characters.")

    print("All EnhancedEnigmaMachine tests have been passed!")

    # Analysis of the key space for the standard EnigmaMachine vs the EnhancedEnigmaMachine     

def number_involutions(n:int) -> int:
    """
    The number of self-inverse permutations (involutions) on n elements where every 
    element either stays fixed or swaps with one other element (Knuth, 1998, p.48).

    Use the recurrence given as Equation (40) by Knuth (1998, p.62)
    I(n) = I(n-1) + (n-1) * I(n-2), I(0) = I(1) = 1 

    This is to quantify the key space if only the reciprocal weakness of the Enigma machine remains,
    so the self-coding weakness is removed. 
    """
    previous, current = 1,1
    for i in range(2, n+1):
        previous, current = current, current + (i-1) * previous
    return current

def number_derangements(n: int) -> int:
    """
    The number of non-self-code permutations (derangements) on n elements:
    permutations where no letter can map to itself. 

    Use the inclusion-exclusion formula given as Equation (5.50) by Graham et al (1994, p.194)
    
    D(n) = sum_{k=0}^{n} (-1)^k * n! / k!

    This is to quantify the key space if only the self-coding weakness of the Enigma machine remains,
    so the reciprocal weakness is removed.  
    """
    # range(n+1) gives k = 0, 1, ..., n inclusive, which is the same as sum_{k=0}^{n} from the formula
    # (-1)**k alternates +/- with each term, which is the inclusion-exclusion correction
    return sum((-1)**k * math.factorial(n) // math.factorial(k) for k in range(n+1))

def standard_enigma_space(n: int) -> int:
    """
    This is the standard enigma key space where both weaknesses are present, no letter can encrypt to itself and,
    the machine encryption is self-inverse.
    Counted by p(n) = (n-1)!! = (n-1)*(n-3)*...*1
    where p(n) = (n-1)*p(n-2) with p(0) = 1

    So a partner is selected for the first letter (n-1 options) and then
    the remaining n-2 letters get paired up (Thimbleby, 2016, pp.183-184). 

    n needs to be even since letters will pair up and if n were odd there would be a letter missing a pair.
    """

    if n % 2 != 0:
        return 0
    return math.prod(range(1,n,2))          # (n-1) * (n-3) *....* 1

def thimbleby_fig_2_test():
    """
    Confirms if the functions defined align with Thimbleby's Figure 2 table (2016, p.185).
    The figure represents different combinations of the two coding weaknesses:
    - self-coding weakness
    - reciprocal weakness
    and their effects on the permutations for a 4 letter sequence. 
    """
    assert math.factorial(4) == 24,         "Should have returned 24 permutations for 4 elements"
    assert number_derangements(4) == 9,     "Expected 9 permutations given that the reciprocal weakness is removed"
    assert number_involutions(4) == 10,     "Expected 10 permutations given that the self-code weakness is removed"
    assert standard_enigma_space(4) == 3,     "Should have returned 3 permutations with both weaknesses present"
    print("All tests from Figure 2 have been validated for 4 letters.")


def key_space_calc():
    """
    Calculates the letter-permutation key space for the standard EnigmaMachine and the EnhancedEnigmaMachine, 
    to quantify the effect that the self-coding and reciprocal coding weaknesses 
    had on the standard machine (Thimbleby, 2016).

    The standard EnigmaMachine has two major weaknesses: no letter can encrypt to itself (self-coding weakness) and 
    encryption is its own inverse (reciprocal weakness). 
    With both of these constraints, the standard machine is limited to only permutations that pair up its 26 letters into
    13 reciprocal, non-self-coding pairs. 
    These count is p(26) = 25*23*21*...*1 (Thimbleby, 2016, pp.183-184).

    Since the EnhancedMachine does not have the same constraints as the standard machine, 
    all 26! letter-substitution permutations are available (Thimbleby, 2016, p.183).

    """
    n = 26 # 26 letters of the alphabet
    both_weaknesses_pres = standard_enigma_space(n)                     # Standard EnigmaMachine with both weaknesses
    reciprocal_only = number_involutions(n)                             # No self-coding weakness
    self_coding_only = number_derangements(n)                           # No reciprocal weakness
    remove_both_weaknesses = math.factorial(n)                          # EnhancedEnigmaMachine

    print("Enigma Machine Key space Comparison")
    print(f"Number of permutations when both weaknesses are present:{both_weaknesses_pres:.3e} ")
    print(f"Number of permutations if self-coding weakness is removed:{reciprocal_only:.3e} (x{reciprocal_only/both_weaknesses_pres:.1f} larger) ")
    print(f"Number of permutations if reciprocal weakness is removed:{self_coding_only:.3e} (x{self_coding_only/both_weaknesses_pres:.3e} larger) ")
    print(f"Number of permutations if neither weakness is present:{remove_both_weaknesses:.3e} (x{remove_both_weaknesses/both_weaknesses_pres:.3e} larger) ")
    print()



  
if __name__ == "__main__":
    enhanced_reflector_testing()
    enhanced_enigma_testing()
    print()
    thimbleby_fig_2_test()
    key_space_calc()



#References
# Thimbleby, H., 2016. Human factors and missed solutions to Enigma design weaknesses. Cryptologia, 40(2), pp.177-202.
# Knuth, D.E., 1998. The art of computer programming, vol. 3: sorting and searching. 2nd ed. Reading, Mass.: Addison Wesley Longman.
# Graham, R.L., Knuth, D.E. and Patashnik, O., 1994. Concrete mathematics: a foundation for computer science. 2nd ed. Reading, Mass.: Addison-Wesley Longman.
         
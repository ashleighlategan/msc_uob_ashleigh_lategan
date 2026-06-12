import math
from enigma import EnigmaMachine, Reflector, ALPHABET
from enigma_enhanced import EnhancedReflector, EnhancedEnigmaMachine

# In the original A reflector wiring E mapped to A and A mapped to E and 
# J mapped to B and B mapped to J
# In the new A wiring, J maps to A but A still maps to E, and
# E maps to B but B still maps to J
NEW_A_WIRING = "JEMZALYXVBWFCRQUONTSPIKHGD"

def enhanced_reflector_testing():
    """Checks that the behaviour of the EnhancedReflector meets expectations."""

    # Construct an instance
    
    enhanced_reflector_name = "New_A"
    ref = EnhancedReflector(enhanced_reflector_name, NEW_A_WIRING)
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
    # We need to check that passing wiring for the refelctor where a letter maps to itself, is accepted

    self_coding_wiring = ALPHABET
    ref_self_code = EnhancedReflector("self-code refelctor", self_coding_wiring)
    assert ref_self_code.encode("A") == "A", ("""A letter should be able to encode to itself using the EnhancedReflector 
                                                  with the necessary wiring provided.""")
        
    print("Test 2 passed showing that the enhanced refelctor does not have the non-self-coding constraint.")

    # Test 3: Removing the reciprocal coding constraint.
    # The standard enigma machine was symmetrical such that encoding and decoding were the same with the same machine settings.
    # For example inputting a character "A" encodes to "D" and at the same settings, "D" then encodes back to "A".
    # The EnhancedEnigmaMachine does not have this feature so encoding a input character and then encoding the output should not return the same input character.
    
    enhanced_reflector_name = "New_A"

    # Two separate machines are required for this test since the relevant rotor(s) advance with each keypress.
    # If the same machine was reused, it would be starting off at the wrong rotor position(s).

    enhanced_machine_1 = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector(enhanced_reflector_name, NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )
    enhanced_machine_2 = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector(enhanced_reflector_name, NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )

    reciprocal_constraint_present = all(enhanced_machine_2.encode_character(enhanced_machine_1.encode_character(c))
                                            == c for c in ALPHABET)
    assert not reciprocal_constraint_present, ("The EnhancedEnigmaMachine's encode is not self-inverse.")

    print("Test 3 passed: The EnhancedEnigmaMachine no longer features the reciprocal coding constraint" )

    # Test 4: Checking decode produces the original input
    # such that decode(encode(text)) == text
    # Like in test 3 we require 2 separate machines to test this, since the relevant rotor(s) will advance with each keypress. 

    encoding_machine = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector(enhanced_reflector_name, NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )
    
    decoding_machine = EnhancedEnigmaMachine(
        rotor_names = ["Beta", 'II', 'V'],
        reflector = EnhancedReflector(enhanced_reflector_name, NEW_A_WIRING),
        ring_settings = [1, 1, 1],
        starting_positions = "AAA",
        )
    
    input_text = "THISISTESTFOUROFTHEENHANCEDENIGMAMACHINE"
    encrypted_text = encoding_machine.encode_string(input_text)
    decrypted_text = decoding_machine.decode_string(encrypted_text)

    assert decrypted_text == input_text, (f""" Decoding the encrypted_text should return {input_text}, 
                                              result was: {decrypted_text}.""")
    
    print("Test 4 passed showing that the separate decode method works to return the input string for the same machine settings")

if __name__ == "__main__":
    enhanced_reflector_testing()
    enhanced_enigma_testing()
         
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
    ref = EnhancedReflector(enhanced_reflector_name, "NEW_A_WIRING")
    assert ref.name == "New_A"
    assert ref.wiring == "NEW_A_WIRING"

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

    
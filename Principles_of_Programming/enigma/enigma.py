
class PlugLead:
    def __init__(self, mapping: str) -> None: 
        """
        A single plug lead that connects two letters on a plugboard.

        :param mapping: A 2-character string for the 2 letters to connect bidirectionally e.g. 'AG' or 'GA' 
        :raises ValueError: If the mapping is not only 2 characters, if they are non-alphabetic characters, or a letter tries to map to itself. 
        """
        if len(mapping) != 2:
            raise ValueError ("A plug lead can only connect 2 characters")
        if not mapping.isalpha():
            raise ValueError("Plug lead mappings are only for alphabetical characters.")
        if mapping[0].upper() == mapping[1].upper():                                        # cater for all cases
            raise ValueError("A plug lead cannot map a letter to itself.")
        self.mapping = mapping.upper()
    
    def __repr__(self) -> str:
        return f"PlugLead('{self.mapping}')"
 
    def encode(self, character:str) -> str:
        """
        Single letter encoding via this lead.

        :param character: Single letter to possibly encode 
        :return: The character it is connected to, if it is connected via this lead, otherwise the character is unchanged.
        """
        character = character.upper()
        if character == self.mapping[0]:
            return self.mapping[1]
        elif character == self.mapping[1]:
            return self.mapping[0]
        else:
            return character


class Plugboard:
    """
    Represents the plugboard which can have a maximum of 10 plug leads.

    Maintains a precomputed bidirectional dictionary for O(1) letter lookup.
    """ 
    TOTAL_LEADS = 10
    
    def __init__(self) -> None:
        """ Initialises an empty plugboard with no plugs connected. """
        self._map: dict[str, str] = {}                                      # precomputed bidirectional dictionary of letter to connected letter, O(1) lookup
    
    def __repr__(self) -> str:
        connects = [f"{k}{v}" for k, v in self._map.items() if k < v]       # k < v to avoid using both directions
        return f"Plugboard(leads={connects})"
    
    def add(self, lead: PlugLead) -> None:
        """
        Add another PlugLead to the plugboard and update the internal lookup dictionary.

        :param lead: PlugLead to add
        :raises ValueError: If the plugboard is already full or if the letter is already connected to another plug.
        """
        if len(self._map) // 2 >= self.TOTAL_LEADS:
            raise ValueError("Plugboard can't have more than 10 leads.")
        
        for letter in lead.mapping:
            if letter in self._map:                                                        # O(1) check against existing dictionary before mapping any letters                                     
                raise ValueError(f"The {letter} is already connected to a plug.")
        # Plugboard connections are bidirectional, need both mappings in dictionary
        self._map[lead.mapping[0]] = lead.mapping[1]
        self._map[lead.mapping[1]] = lead.mapping[0]

    def encode(self, character: str) -> str:
        """
        Encode a letter using the plugboard.

        :param character: Single letter to possibly encode.
        :return: The connected letter if it is part of a lead, else it returns the letter unchanged. 
        """
        return self._map.get(character.upper(), character.upper())
    
    
# Enigma Machine Constants: alphabet, rotor and reflector wiring settings, and notch positions for each rotor. 

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHA_TO_IDX= {c: i for i, c in enumerate(ALPHABET)}    # O(1) alphabet character to index lookup

ROTOR_WIRING = {
    "Beta":  "LEYJVCNIXWPBQMDRTAKZGFUHOS",              # Rotors Beta, Gamma and I-V
    "Gamma": "FSOKANUERHMBTIYCWLQPZXVGJD",
    "I":     "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":    "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III":   "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV":    "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V":     "VZBRGITYUPSDNHLXAWMJQOFECK",
    "A":     "EJMZALYXVBWFCRQUONTSPIKHGD",              # reflector A, B, C
    "B":     "YRUHQSLDPXNGOKMIEBFZCWVJAT", 
    "C":     "FVPJIAOYEDRZXWGCTKUQSBNMHL",  
}

ROTOR_NAMES = frozenset({"Beta", "Gamma", "I", "II", "III", "IV", "V"})
REFLECTOR_NAMES = frozenset({"A", "B", "C"})

# Notch positions for rotors I to V (when rotor is at its notch, the next keypress triggers the rotor to its left)
ROTOR_NOTCH = {"I": "Q", "II": "E", "III": "V", "IV": "J", "V": "Z"}
    
class Rotor:
    """
    One Enigma rotor with position, ring setting and possible turnover notch.

    Position: visible letter shown on rotor window, stored as a 0-25 integer
    Ring setting: shifts the internal wiring relative to external markings input as 1-26 integer but stored as 0-25.

    Encoding formula:
        shifted = (input_index + position - ring_offset) % 26
        output = (wired_index - position + ring_offset) % 26
    This adds the position offset on entry and reverses it on exit
    and the ring offset shifts the wiring in the opposite direction.

    """
    def __init__(self, name: str, position: str = "A", ring_setting: int = 1) -> None:
        """
        :param name: Rotor name e.g. 'Gamma', 'III' 
        :param position: Starting letter (defaults to 'A')
        :param ring_setting: Ring setting 1-26 (default 1, no offset)
        :raises ValueError: If an invalid rotor name is used
        :raises ValueError: If an invalid position is provided
        :raises ValueError: If an invalid ring setting is used
        """
        if name not in ROTOR_NAMES:
            raise ValueError(f"Unknown rotor name {name!r} used. Must be Beta, Gamma, I, II, III, IV or V.")
        if len(position) != 1 or not position.isalpha():
            raise ValueError(f"Invalid rotor position {position!r} provided, rotor position should be one alphabetical letter of any case.")
        if not isinstance(ring_setting, int) or not (1 <= int(ring_setting) <= 26):
            raise ValueError(f"Invalid ring setting {ring_setting!r} provided, ring setting should be a single integer from 1 to 26.")
        self.name = name
        self.wiring = ROTOR_WIRING[name]
        self.reverse_wiring =  {c:i for i,c in enumerate(self.wiring)}  # maps each character to its position in the wiring string for O(1) left-to-right lookup
        self.position = ALPHA_TO_IDX[position.upper()]                  # converts to int, 0-25
        self.ring_offset = ring_setting -1                              # converts from 1-26 to 0-25
        self.notch = ROTOR_NOTCH.get(name)
    
    def __repr__(self) -> str:
        return f"Rotor(name='{self.name}', position='{ALPHABET[self.position]}', ring_setting={self.ring_offset + 1})"
    
    def reached_notch(self) -> bool:
        """ True if the rotor is currently at its turnover notch position """
        return self.notch is not None and ALPHABET[self.position] == self.notch
    
    def rotate(self) -> None:
        """ Rotate the rotor by one position (triggered by key press) """
        self.position = (self.position + 1) % 26
    
    def encode_right_to_left(self, character: str) -> str:   
        """ Encode input character passing from the rightmost rotor to the leftmost rotor (towards reflector) """
        alpha_idx = ALPHA_TO_IDX[character.upper()]
        shifted = (alpha_idx + self.position - self.ring_offset) % 26
        wired = ALPHA_TO_IDX[self.wiring[shifted]]
        output = (wired - self.position + self.ring_offset) % 26
        return ALPHABET[output]  
    
    def encode_left_to_right(self, character: str) -> str:
        """ Encode input character passing from the leftmost rotor to the rightmost rotor (away from reflector)"""
        alpha_idx = ALPHA_TO_IDX[character.upper()]
        shifted = (alpha_idx + self.position - self.ring_offset) % 26
        wired = self.reverse_wiring[ALPHABET[shifted]]
        output = (wired - self.position + self.ring_offset) % 26
        return ALPHABET[output]         

class Reflector:
    """
    The Enigma reflector: a fixed substitution where each letter maps
    to a different letter AND the mapping is self-inverse (A->Y means Y->A). 

    This is what ensures encryption and decryption use the same keypress:
    pressing A can never encrypt to A (the machine could never encrypt a
    letter as itself).

    The standard reflectors are 'A', 'B' or 'C' but a user may want to use a non-standard reflector with custom wiring, 
    if they do then this will override the standard reflector wiring. 
    """
    def __init__(self, name:str, non_standard_wiring:str|None = None) -> None:
        """
        :param name: Reflector name: "A", "B" or "C".
        :param non_standard_wiring: Optional custom wiring that is used if provided. 
        :raises ValueError: If the name is not a valid reflector name and only standard wiring was provided.
        :raises ValueError: If the non-standard reflector wiring is not exactly 26 characters.
        :raises ValueError: If the non-standard reflector wiring do not only contain alphabetical characters.
        :raises ValueError: If the non-standard reflector wiring is not a permutation of the 26 alphabetical letters A to Z.
        :raises ValueError: If the non-standard reflector wiring attempts to encode a letter to itself
        """
        if non_standard_wiring is not None:
            non_standard_wiring = non_standard_wiring.upper()
            if len(non_standard_wiring) !=26:
                raise ValueError("Reflector wiring needs to be exactly 26 letters.")
            if not non_standard_wiring.isalpha():
                raise ValueError("Reflector wiring needs to only consist of alphabetical letters.")
            if set(non_standard_wiring) != set(ALPHABET):
                raise ValueError("Reflector wiring must be a permutation of the alphabet, A-Z.")
            # In the standard reflector no letter can map to itself
            for i, maps in enumerate(non_standard_wiring):
                if maps == ALPHABET[i]:
                    raise ValueError("Reflector wiring cannot map the same letter to itself.")
            self.name = name
            self.wiring = non_standard_wiring
        else:
            if name not in REFLECTOR_NAMES:
                raise ValueError(f"Unknown reflector name {name} used. Must be A, B or C.") 
            self.name = name
            self.wiring = ROTOR_WIRING[name]
   
    def __repr__(self) -> str:
        return f"Reflector('{self.name}')"

    def encode(self, character: str) -> str:
        """ Encode input character through the reflector's wiring.
        
        :param character: Single uppercase or lowercase letter to encode.
        :return: The matching letter based on its wiring.  
        """
        return self.wiring[ALPHA_TO_IDX[character.upper()]]
    
def rotor_from_name(name:str) -> Rotor:        
    """ 
    Create a Rotor from name, with default position and ring setting

    :param name: Rotor name e.g. "I", "Beta" 
    :return: Rotor instance at position 'A' and ring setting 1
    """                                      
    return Rotor(name)    
                                           
class EnigmaMachine:  
    """
    A complete Enigma machine with the plugboard, rotors and a reflector.

    Rotors are given left-to-right, as you would see looking at the machine 
    e.g ["I", "II", "III"] where III is the rightmost rotor. 
    The electrical signal moves right-to-left through the rotors, hits the reflector 
    and then moves back left-to-right through the rotors.

    Rotation(s) following a keypress:
    1. The rightmost rotor always steps.
    2. If the rightmost is at its notch, the middle rotor will also step.
    3. If the middle rotor is at its notch, it steps again (double-step) and triggers the next rotor to also step.
    Note: In a 4-rotor machine, the leftmost rotor never steps. 
    """   
    def __init__(self, 
                 rotor_names: list[str],
                 reflector: Reflector,
                 ring_settings: list[int],
                 starting_positions: str,
                 plugboard_pairs: list[str] | None = None,
                 ) -> None:
        """
        :param rotor_names: Left-to-right rotor names e.g. ["Beta", "III", "V"].
        :param reflector: Reflector instance (either a standard one 'A', 'B' or 'C' or a custom one with non-standard wiring).
        :param ring_settings: Ring settings 1 to 26 for the rotors from left to right.
        :param starting_positions: Starting position as letters, for each rotor e.g. "AAZ".
        :param plugboard_pairs: Optional list of 2-char plug pairs e.g ["CT", "EZ"].
        :raises ValueError: If the number of rotors is not 3 or 4.
        :raises ValueError: If the rotors provided are not unique. 
        :raises ValueError: If the number of ring settings is not equivalent to the number of rotors.
        :raises ValueError: If the number of starting positions is not equivalent to the number of rotors.
        """
        if len(rotor_names) not in (3,4):
            raise ValueError("Enigma machines require 3 or 4 rotors.")
        if len(rotor_names) != len(set(rotor_names)):
            repeated_rotors = {name for name in rotor_names if rotor_names.count(name) > 1}
            raise ValueError(f"Enigma machines can only use each valid rotor once, please correct the repeated rotors: {repeated_rotors}")
        if len(ring_settings) != len(rotor_names):
            raise ValueError("Need to supply ring setting for each rotor.")
        if len(starting_positions) != len(rotor_names):
            raise ValueError("Need to supply starting position for each rotor.")
        
        self.rotors = [ 
            Rotor(name, pos, ring_set)
            for name, pos, ring_set in zip(rotor_names, starting_positions, ring_settings)
        ]

        self.reflector = reflector

        self.plugboard = Plugboard()
        for pair in (plugboard_pairs or []):
            self.plugboard.add(PlugLead(pair))
    
    def __repr__(self) -> str:
        return f"""EnigmaMachine(
        rotors={self.rotors},
        reflector={self.reflector},
        plugboard={self.plugboard}
        )"""
    
    def _step_rotors(self) -> None:
        """
        Advance the rotors according to the stepping mechanism,
        including the double-stepping mechanism for the middle rotor(s).
        """

        n = len(self.rotors)
        step = [False] * n                                      # one entry per rotor, tracks which rotors should step on this keypress
        step[-1] = True                                         # rightmost rotor always steps

        if n >= 2: 
            if self.rotors[-1].reached_notch():
                step[-2] = True                                 # rightmost rotor at notch, triggers next rotor to step                   
            if self.rotors[-2].reached_notch():
                step[-2] = True                                 # double-step
                if n >= 3:
                    step[-3] = True                             # triggers step of 3rd rotor (this is the leftmost rotor that can step)
        
        for i, to_step in enumerate(step):
            if to_step:
                self.rotors[i].rotate() 

    def encode_character(self, character: str) -> str:
        """
        Encodes a single character using the Enigma machine:
        plugboard -> rotors (right to left) -> reflector -> rotors (left to right) -> plugboard
        Rotors will step before the signal passes through them. 

        :param character: An uppercase or lowercase letter
        :return: Encoded uppercase letter
        """

        character = character.upper()
        if character not in ALPHABET:
            raise ValueError(f"Character '{character}' is not a valid alphabetical letter A-Z.")
        
        self._step_rotors()

        signal = self.plugboard.encode(character)

        for rotor in reversed(self.rotors):                     # reversed works through the rotor list from right to left
            signal = rotor.encode_right_to_left(signal)

        signal = self.reflector.encode(signal)                  # reflector

        for rotor in self.rotors:                               # rotors are stored left to right so no reversed needed
            signal = rotor.encode_left_to_right(signal)

        return self.plugboard.encode(signal) 

    def encode_string(self, text:str) -> str:
        """
        Encode a string of characters, still advancing the relevant rotors with each keypress. 
        Any non-alphabetical characters are ignored as the Enigma machine only processes letters.
        
        :param text: Encrypted or decrypted text of any case
        :return: Encoded or decoded uppercase text
        """
        return "".join(self.encode_character(c) for c in text.upper() if c in ALPHABET)

if __name__ == "__main__":
    # You can use this section to write tests and demonstrations of your enigma code.
    # TESTING THE PLUGLEAD:
    # ---------------------------------------------
    # Lowercase mapping should work as uppercase
    lead = PlugLead("ag")
    assert lead.encode("A") == "G"
    assert lead.encode("G") == "A"

    # All letters that aren't connected should pass through unchanged
    lead = PlugLead("AG")
    for char in "BCDEFHIJKLMNOPQRSTUVWXYZ":
        assert lead.encode(char) == char

    # Error cases - these should all raise ValueError
    try:
        lead = PlugLead("AA")  # connecting a letter to itself
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        lead = PlugLead("H")  # too short
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        lead = PlugLead("XYZ")  # too long
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        lead = PlugLead("J3")  # number in mapping
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        lead = PlugLead("W!")  # special character
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("All PlugLead tests passed!")

    # TESTING THE PLUGBOARD:
    # ---------------------------------------------
    plugboard = Plugboard()
    plugboard.add(PlugLead("FJ"))
    plugboard.add(PlugLead("KN"))

    # Basic encoding both ways
    assert plugboard.encode("F") == "J"
    assert plugboard.encode("J") == "F"
    assert plugboard.encode("K") == "N"
    assert plugboard.encode("N") == "K"

    # Unconnected letter passes through unchanged
    assert plugboard.encode("Z") == "Z"

    # Lowercase input should still work
    assert plugboard.encode("f") == "J"

    # Duplicate letter should raise an error
    try:
        plugboard.add(PlugLead("FX"))  # F is already used
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Too many leads should raise an error
    pb = Plugboard()
    for plugs in ["AB", "CD", "EF", "GH", "IJ", "KL", "MN", "OP", "QR", "ST"]:
        pb.add(PlugLead(plugs))
    try:
        pb.add(PlugLead("UV"))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("All Plugboard tests passed!")

    # TESTING THE ROTOR:
    # ---------------------------------------------
    
    # Test encoding with rotor set to default position and ring settings. 
    rotor = rotor_from_name("II")
    assert(rotor.encode_right_to_left("C") == "D")
    assert(rotor.encode_left_to_right("C") == "P")

    # Encoding with a non-default position to test the offset logic in both directions.
    rotor = Rotor("I", position="B")
    # Position B (index 1): input A hits pin B, wiring[1] = K, output shifted back by 1 = J
    assert(rotor.encode_right_to_left("A") == "J")
    # Position B (index 1): input A hits pin B, reverse_wiring[B] = 22 or W , output shifted back by 1 = V
    assert(rotor.encode_left_to_right("A") == "V")

    # Non-default ring setting — ring 2 shifts wiring in opposite direction to position.
    # Rotor with Ring 2 at position A is the same as setting it to ring 1 at position Z (one step back).
    # Both directions are tested to confirm the offset applies symmetrically.
    rotor_ring_2 = Rotor("I", position="A", ring_setting=2)
    rotor_pos_Z  = Rotor("I", position="Z", ring_setting=1)
    for c in ALPHABET:
        assert rotor_ring_2.encode_right_to_left(c) == rotor_pos_Z.encode_right_to_left(c)
        assert rotor_ring_2.encode_left_to_right(c) == rotor_pos_Z.encode_left_to_right(c)
    
    # Encoding should be self-inverse: right-to-left followed by left-to-right should return the original.
    # This should hold for any rotor position or ring combination.
    for name in ["I", "II", "III", "IV", "V", "Beta", "Gamma"]:
        rotor = Rotor(name, position="D", ring_setting=7)
        for c in ALPHABET:
            assert rotor.encode_left_to_right(rotor.encode_right_to_left(c)) == c
    
    # reached_notch() test for rotor V which notches at Z
    rotor = Rotor("V", position="Z")
    assert rotor.reached_notch() is True
    rotor = Rotor("V", position="Y")
    assert rotor.reached_notch() is False

    # Check that the Notchless rotors (Beta, Gamma) don't ever report reaching a notch
    for a in ALPHABET:
        assert Rotor("Beta", position= a).reached_notch() is False
        assert Rotor("Gamma", position= a).reached_notch() is False

    # rotate() advances the position by one, and wraps Z back to A due to modulo
    rotor = Rotor("I", position="D")
    rotor.rotate()
    assert ALPHABET[rotor.position] == "E"

    rotor = Rotor("I", position="Z")
    rotor.rotate()
    assert ALPHABET[rotor.position] == "A"

    # Invalid Rotor name should raise a ValueError
    try:
        Rotor("X")
        assert False, "Invalid Rotor name, should have raised ValueError"
    except ValueError:
        pass

    print("All Rotor tests passed!")

    # TESTING THE REFLECTOR:
    # ---------------------------------------------

    # Testing each reflector for a single input:
    assert Reflector("A").encode("H") == "X"
    assert Reflector("B").encode("G") == "L"
    assert Reflector("C").encode("E") == "I"

    # Reflector is self-inverse: encoding twice should return the original letter.
    # This is a core property of Enigma and it is what makes encryption and decryption symmetrical.
    for name in ["A", "B", "C"]:
        reflector = Reflector(name)
        for c in ALPHABET:
            assert reflector.encode(reflector.encode(c)) == c
    
    # A letter can never map to itself, useful to test our wiring is correct:
    for name in ["A", "B", "C"]:
        reflector = Reflector(name)
        for c in ALPHABET:
            assert reflector.encode(c) != c

    # Test that a lowercase input works
    reflector = Reflector("B")
    assert reflector.encode("c") == "U"

    # Invalid Reflector name should raise a ValueError
    try:
        Reflector("F")
        assert False, "Invalid Reflector name, should have raised ValueError"
    except ValueError:
        pass

    # Non_standard_wiring Testing:

    # Using a valid non_standard_wiring string
    custom_ref = Reflector("custom", "GQMWJEIFNOZPVLBUTXRSAKCYHD")
    assert custom_ref.encode("A") =="G"
    assert custom_ref.encode("D") =="W"

    # No letter should map to itself for the standard Enigma machine reflector wiring
    for c in ALPHABET:
        assert custom_ref.encode(c) != c

    # Using self-coding reflector wiring should raise a ValueError
    try:
        Reflector("self_code_ref", "QCYLXWDVZRIOUGEMKTSNAPJBHF")                            # S maps to itself
        assert False, "Should have raised a ValueError for self-coding reflector wiring."
    except ValueError:
        pass

    # Wiring that does not contain 26 alphabetical letters
    try:
        Reflector("short_ref", "QCYLX")
        assert False, "Wiring that is no 26 alphabetical letters long, should raise a ValueError"
    except ValueError:
        pass

    # Wiring that contains non-alphabetical character(s) should raise a ValueError
    try:
        Reflector("non_alpha_ref","5JMZALYXVBWFCRQUONTSPIKHGD")                             # 5 instead of the letter E
        assert False, "Wiring that does not contain 26 alphabetical characters should raise a ValueError"
    except ValueError:
        pass

    # Wiring that contains repeat letters

    try:
        Reflector("repeat_ref", "EJMZELYXVBWFCRQUONTSPIKHGD")                                # 2 Letter Es
        assert False, "Wiring should only have 1 character for each letter of the alphabet, A-Z"
    except ValueError:
        pass

    print("All Reflector tests passed!")

    # TESTING THE ENIGMA MACHINE:
    # ---------------------------------------------

    # INSTANTIATION TESTING: 

    # Incorrect number of rotors should raise an error
    try:
        EnigmaMachine(rotor_names = ["I", "V"], reflector= Reflector("B"), ring_settings = [1, 1], starting_positions = "AA")
        assert False, "Incorrect number of Rotors provided, should have raised ValueError"
    except ValueError:
        pass
    # Incorrect number of ring settings provided for the number of rotors, should raise an error:
    try:
        EnigmaMachine(rotor_names=["I", "II", "III"], reflector= Reflector("A"), ring_settings=[1, 1], starting_positions="AAA")
        assert False, "Incorrect number of ring settings provided, should have raised ValueError"
    except ValueError:
        pass
     # Incorrect number of starting positions provided for the number of rotors, should raise an error:
    try:
        EnigmaMachine(rotor_names=["I", "II", "IV"], reflector= Reflector("C"), ring_settings=[1, 1, 1], starting_positions="AB")
        assert False, "Incorrect number of starting positions provided, should have raised ValueError"
    except ValueError:
        pass

    # ENCODING TESTING: 

    # We cannot encode non-alphabetical characters, this should raise an error
    try:
        machine = EnigmaMachine(rotor_names=["I", "II", "IV"], reflector= Reflector("B"), ring_settings=[1, 1, 1], starting_positions="AAA")
        machine.encode_character("3")
        assert False, "Non-alphabetic character should have raised ValueError"
    except ValueError:
        pass

    # Self-inverse testing where we would expect that encoding the output should return the original character
    # We have to use to machine instances set at the same setting as using the same machine wouldn't work since the rotor(s) rotate
    enigma_machine_1 = EnigmaMachine(rotor_names=["I", "II", "III"], reflector= Reflector("B"), ring_settings=[1, 1, 1], starting_positions="AAA")
    enigma_machine_2 = EnigmaMachine(rotor_names=["I", "II", "III"], reflector= Reflector("B"), ring_settings=[1, 1, 1], starting_positions="AAA")
    for c in ALPHABET:
        assert enigma_machine_2.encode_character(enigma_machine_1.encode_character(c)) == c
    
    # Encoding a string containing any non-alphabetical characters will just skip them and not fail
    enigma_machine_1 = EnigmaMachine(rotor_names=["I", "II", "III"], reflector= Reflector("A"), ring_settings=[1, 1, 1], starting_positions="ACD")
    enigma_machine_2 = EnigmaMachine(rotor_names=["I", "II", "III"], reflector= Reflector("A"), ring_settings=[1, 1, 1], starting_positions="ACD")
    assert enigma_machine_1.encode_string("HE LLO") == enigma_machine_2.encode_string("HELLO")

    # If we have 3 rotors set at ADU then after 3 keystrokes should have ADV, AEW and BFX rotor positions
    # Start at ADU as U is just before Rotor III's notch at V 
    # We also then hit AEW after 1 keypress and E is Rotor II's notch so we can test the double-step
    # Confirmed with the Enigma Machine Emulator: https://www.101computing.net/enigma-machine-emulator/
    enigma_machine = EnigmaMachine(rotor_names=["I", "II", "III"], reflector= Reflector("C"), ring_settings=[1, 1, 1], starting_positions="ADU")
    positions = []
    for _ in range(3):
        enigma_machine.encode_character("A")
        positions.append("".join(ALPHABET[r.position] for r in enigma_machine.rotors))
    assert positions == ["ADV", "AEW", "BFX"]

    print("All EnigmaMachine tests passed!")

    # TESTING __repr__:
    # ---------------------------------------------

    assert repr(PlugLead("DT")) == "PlugLead('DT')"

    # Empty Plugboard
    assert repr(Plugboard()) == "Plugboard(leads=[])"
    # Non-empty Plugboard
    pb_test = Plugboard()
    pb_test.add(PlugLead("FN"))
    assert repr(pb_test) == "Plugboard(leads=['FN'])"

    # Rotor
    assert repr(Rotor("III", "E", 3)) == "Rotor(name='III', position='E', ring_setting=3)"
    
    # Reflector
    assert repr(Reflector("C")) == "Reflector('C')"

    # EnigmaMachine
    assert repr(EnigmaMachine(["Gamma", "V", "I"], Reflector("C"), [2,1,1], "AAZ"))

    print("All __repr__ tests have passed!")


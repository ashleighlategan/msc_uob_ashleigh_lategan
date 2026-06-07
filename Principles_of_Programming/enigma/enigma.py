
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
    TOTAL_LEADS = 10
    
    def __init__(self) -> None:
        """
        Represents the plugboard which can have a maximum of 10 PlugLead objects.

        Maintains a precomputed bidirectional dictionary for O(1) letter lookup.
        """ 
        self.leads: list[PlugLead] =[]          # empty list to start, leads get added via add()
        self._map: dict[str, str] = {}          # precomputed bidirectional dictionary, O(1) lookup
    
    def add(self, lead: PlugLead) -> None:
        """
        Add another PlugLead to the plugboard and update the internal lookup dictionary.

        :param lead: PlugLead object to add
        :raises ValueError: If the plugboard is already full or if the letter is already connected to another plug.
        """
        if len(self.leads) >= self.TOTAL_LEADS:
            raise ValueError("Plugboard can't have more than 10 leads.")
        
        for letter in lead.mapping:
            if letter in self._map:                                                        # 0(1) check against existing dictionary                                      
                raise ValueError(f"The {letter} is already connected to another plug.")
        self.leads.append(lead)         # a lead is only added if all checks pass

        # Plugboard connections are bidirectional, need both mappings in dictionary
        self._map[lead.mapping[0]] = lead.mapping[1]
        self._map[lead.mapping[1]] = lead.mapping[0]



    def encode(self, character: str) -> str:
        """
        Encode a letter using the plugboard.

        :param character: Single letter to possibly encode ]
        :return: The connected letter if it is part of a lead, else it returns the letter unchanged. 
        """
        return self._map.get(character.upper(), character.upper())
    
# Enigma Machine Constants: alphabet, rotor and reflector wiring settings, and notch positions for each rotor. 

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ROTOR_WIRING = {
    "Beta":  "LEYJVCNIXWPBQMDRTAKZGFUHOS", # Rotors Beta, Gamma and I-V
    "Gamma": "FSOKANUERHMBTIYCWLQPZXVGJD",
    "I":     "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":    "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III":   "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV":    "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V":     "VZBRGITYUPSDNHLXAWMJQOFECK",
    "A":     "EJMZALYXVBWFCRQUONTSPIKHGD",  # reflector A, B, C
    "B":     "YRUHQSLDPXNGOKMIEBFZCWVJAT", 
    "C":     "FVPJIAOYEDRZXWGCTKUQSBNMHL",  
}

# Notch positions for rotors I to V (when rotor is at its notch, the next keypress triggers the rotor to its left)
ROTOR_NOTCH = {"I": "Q", "II": "E", "III": "V", "IV": "J", "V": "Z"}
    
class Rotor:
    """
    One Enigma rotor with position, ring setting and possible turnover notch.

    Position: visible letter shown on rotor window (0-25 integer)
    Ring setting: shifts the internal wiring relative to external markings (1-26 integer)

    Encoding formula:
        shifted = (input_index + position - ring_offset) % 26
        output = (wired_index - position + ring_offset) % 26
    This adds the position offset on entry and reverses it on exit
    and the ring offset shifts the wiring in th opposite direction.

    """
    def __init__(self, name: str, position: str = "A", ring_setting: int = 1) -> None:
        """
        :param name: Rotor name e.g. 'Gamma', 'III' 
        :param position: Starting letter (defaults to 'A')
        :param ring setting: Ring setting 1-26 (default 1 (no-offset))
        """
        if name not in ROTOR_WIRING:
            raise ValueError(f"Unknown rotor name {name} used. Must be Beta, Gamma or I-V.")
        self.name = name
        self.wiring = ROTOR_WIRING[name]
        self.position = ALPHABET.index(position.upper())              # converts to int, 0-25
        self.ring_offset = ring_setting -1                            # converts from 1-26 to 0-25
        self.notch = ROTOR_NOTCH.get(name)
    
    def reached_notch(self) -> bool:
        """ True if the rotor is currently at its turnover notch position """
        return self.notch is not None and ALPHABET[self.position] == self.notch
    
    def rotate(self) -> None:
        """ Rotate the rotor by one position (triggered by key press) """
        self.position = (self.position + 1) % 26
    
    def encode_right_to_left(self, character: str) -> str:   
        """ Encode input character passing from the rightmost rotor to the leftmost rotor (towards reflector) """
        alpha_idx = ALPHABET.index(character.upper())
        shifted = (alpha_idx + self.position - self.ring_offset) % 26
        wired = ALPHABET.index(self.wiring[shifted])
        output = (wired - self.position + self.ring_offset) % 26
        return ALPHABET[output]  
    
    def encode_left_to_right(self, character: str) -> str:
        """ Encode input character passing from the leftmost rotor to the rightmost rotor (away from reflector)"""
        alpha_idx = ALPHABET.index(character.upper())
        shifted = (alpha_idx + self.position - self.ring_offset) % 26
        wired = self.wiring.index(ALPHABET[shifted])
        output = (wired - self.position + self.ring_offset) % 26
        return ALPHABET[output]

def rotor_from_name(name:str) -> Rotor:        
    """ Function creates a rotor from name, with default position and ring setting"""                                      
    return Rotor(name)             

class Reflector:
    """
    The Enigma reflector: a fixed substitution where each letter maps
    to a different letter AND the mapping is self-inverse (A->Y means Y->A). 

    This is what ensures encryption and decryption use the same keypress:
    pressing A can never encrypt to A (the machine could never encrypt a
    letter as itself).
    """
    def __init__(self, name:str) -> None:
        if name not in ("A", "B", "C"):
            raise ValueError(f"Unknown reflector name {name} used. Must be A, B or C.") 
        self.name = name
        self.wiring = ROTOR_WIRING[name]
    
    def encode(self, character: str) -> str:
        return self.wiring[ALPHABET.index(character.upper())]
                                           
class EnigmaMachine:  
    """
    A complete Enigma machine demonstration with the plugboard, rotors and a reflector.

    Rotors are given left-to-right, as you would see looking at the machine 
    e.g ["I", "II", "III"]where III is the rightmost rotor. 
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
                 reflector_name: str,
                 ring_settings: list[int],
                 starting_positions: str,
                 plugboard_pairs: list[str] | None = None,
                 ) -> None:
        """
        :param rotor_names: Left-to-right rotor names e.g. ["Beta", "III", "V"]
        :param reflector_name: Reflector name: "A", "B" or "C"
        :param ring_settings: Ring settings 1 to 26 for the rotors from left to right
        :param starting_positions: Starting position as letters, for each rotor e.g. "AAZ"
        :param plugboard_pairs: Optional list of 2-char plug pairs e.g ["CT", "EZ"]
        """
        if len(rotor_names) not in (3,4):
            raise ValueError("Enigma machines require 3 or 4 rotors.")
        if len(ring_settings) != len(rotor_names):
            raise ValueError("Need to supply ring setting for each rotor.")
        if len(starting_positions) != len(rotor_names):
            raise ValueError("Need to supply starting position for each rotor.")
        
        self.rotors = [ 
            Rotor(name, pos, ring_set)
            for name, pos, ring_set in zip(rotor_names, starting_positions, ring_settings)
        ]

        self.reflector = Reflector(reflector_name)

        self.plugboard = Plugboard()
        for pair in (plugboard_pairs or []):
            self.plugboard.add(PlugLead(pair))
    
    def _step_rotors(self) -> None:
        """
        Advance the rotors according to the stepping mechanism.
        Called once ahead of each character being encoded. 
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
        : return: Encoded uppercase letter
        """

        character = character.upper()
        if character not in ALPHABET:
            raise ValueError(f"Character '{character}' is not a valid alphabetical letter A-Z.")
        
        self._step_rotors()

        signal = self.plugboard.encode(character)

        for rotor in reversed(self.rotors):                     # right to left
            signal = rotor.encode_right_to_left(signal)

        signal = self.reflector.encode(signal)                  # reflector

        for rotor in self.rotors:                               # left to right
            signal = rotor.encode_left_to_right(signal)

        return self.plugboard.encode(signal) 

    def encode_string(self, text:str) -> str:
        """
        Encode a string of characters, still advancing the relevant rotors with each keypress. 
        
        :param text: Encrypted or decrypted text (alphabetical letters of any case)
        : return: Encoded or decoded uppercase text
        """
        return "".join(self.encode_character(c) for c in text.upper() if c in ALPHABET)

# You will need to write more classes, which can be done here or in separate files, you choose.


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
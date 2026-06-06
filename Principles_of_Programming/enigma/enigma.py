
class PlugLead:
    def __init__(self, mapping: str) -> None: 
        """
        A single plug lead that connects two letters on a plugboard.
        :param mapping: A 2 character string for the 2 letters that connect e.g. AG 
        """
        if len(mapping) != 2:
            raise ValueError ("A plug lead can only connect 2 characters")
        if mapping[0] == mapping[1]:
            raise ValueError("A plug lead cannot map a letter to itself.")
        if not mapping.isalpha():
            raise ValueError("Plug lead mappings are only for letters.")
        self.mapping = mapping.upper()
 
    def encode(self, character:str) -> str:
        """
        Single letter encoding via this lead.
        If it is connected to another letter that letter is returned, else the character is unchanged.
        :param character: Single letter to possibly encode 
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
        """
        self.leads =[]          # empty list to start, leads get added via add()
    
    def add(self, lead: PlugLead) -> None:
        """
        Add another PlugLead to the plugboard.
        :param lead: PlugLead object to add
        """
        if len(self.leads) >= self.TOTAL_LEADS:
            raise ValueError("Plugboard can't have more than 10 leads.")
        
        # Check that the letters are not already being used:
        used_letters = set()                                # Gather every letter already used by existing leads into a set
        for used_lead in self.leads:
            used_letters.add(used_lead.mapping[0])
            used_letters.add(used_lead.mapping[1])
        
        for letter in lead.mapping:
            if letter in used_letters:
                raise ValueError(f"The {letter} is already connected to another plug.")
        
        self.leads.append(lead)         # a lead is only added if all checks pass
    
    def encode(self, character: str) -> str:
        """
        Passes a character to the plugboard and checks with each PlugLead one by one.
        Returns character unchanged if it is not part of a lead. 
        :param character: Single letter to possibly encode 
        """
        character = character.upper()
        for lead in self.leads:
            output = lead.encode(character)
            if output != character:
                return output
        return character              # character is unchanged if no lead is connected to it
    
    # Wiring patterns: index = input letter (A=0) and value = output letter 

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
            raise ValueError(f"Unknown rotor name {name} used. Must be Beta, Gamma or I-IV.")
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
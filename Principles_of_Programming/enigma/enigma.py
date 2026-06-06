
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
    
class Rotor:
    def __init__(self,name):
        self.wiring= ROTOR_WIRING[name]
    
    def encode_right_to_left(self,character):               
        return self.wiring[ALPHABET.index(character.upper())]          # matches input character to alphabetical character position, passes this to wiring
    
    def encode_left_to_right(self, character):
        return ALPHABET[self.wiring.index(character.upper())]
    
def rotor_from_name(name):                                              # simplification for users, can call rotor_from_name("I") instead of Rotor("I")
    return Rotor(name)                                                 
        


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
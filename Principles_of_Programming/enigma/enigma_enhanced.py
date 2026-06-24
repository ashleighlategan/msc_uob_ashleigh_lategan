from enigma import (Reflector, EnigmaMachine, ALPHABET)

class EnhancedReflector(Reflector):
    """ 
    A non-standard Enigma reflector that takes in any permutation of 26-letters. 

    The standard Enigma Reflector could not have a letter map to itself e.g. B couldn't map to B and 
    in encoding in the standard machine was self-inverse so B-S and S-B. 
    These were both caused by the shared key/lamp wire in the Enigma Machine hardware (Thimbleby, 2016, p.189)

    If we remove these constraints, then encode and decode are separate operations. 

    Reference: Thimbleby, H., 2016. Human factors and missed solutions to Enigma design weaknesses. Cryptologia, 40(2), pp.177-202.

    """

    def __init__(self, name:str, wiring: str) -> None:
        """
        :param name: The name of the reflector e.g. 'A_enhanced'
        :param wiring: The 26-letter permutation string where each letter A-Z appears only once. 
        :raises ValueError: If the wiring does not contain exactly 26 characters. 
        :raises ValueError: If the wiring does not contain only alphabetical characters. 
        :raises ValueError: If the wiring is not a permutation of the 26 alphabetical letters A to Z
        """
        wiring = wiring.upper()
    
        if len(wiring) != 26:
            raise ValueError("Reflector wiring needs to be exactly 26 letters.")
        if not wiring.isalpha():
            raise ValueError("Reflector wiring can only contain alphabetic characters.")
        if set(wiring) != set(ALPHABET):
            raise ValueError("Reflector wiring must be a permutation of the alphabet, A-Z.")
    
        # Set attributes directly for this sub-class to skip the stricter superclass logic that only checks for REFLECTOR_NAMES 'A', 'B' or 'C'
        self.name = name
        self.wiring = wiring 

        # The standard reflector's wiring is self-inverse (encode(encode(c)) == c for all alphabetical letters), so
        # it could leverage encode on both the forward and reverse signal paths.
        # This EnhancedReflector is not self-inverse so we need to define a decode method for the return path
        # If wiring[3] == 'A' then inverse_wiring['A'] == ALPHABET[3] == 'D'

        self.inverse_wiring: dict[str, str] = {char: ALPHABET[i] for i, char in enumerate(wiring)}

    def __repr__(self) -> str:
        return f"EnhancedReflector(name='{self.name}', wiring='{self.wiring}')"    
        
    def decode(self, character: str) -> str:
        """
        Leverage the inverse of the Reflector's wiring to decode a character. 
        The standard machine did not require this because its encode() was self-inverse.

        E.g If encode('A') == 'J', encode('J') != 'A' so a separate decode is required. 

        :param character: A single letter of any case.
        :return: The inverse mapping for the letter.
        """
        return self.inverse_wiring[character.upper()]    
        
class EnhancedEnigmaMachine(EnigmaMachine):
    """
    An updated EnigmaMachine that no longer has the reciprocal weakness of the standard machine (Thimbleby, 2016).

    The rotor functionality is the same as the original EnigmaMachine which is the superclass here. 
    This machine uses an enhanced reflector that is not self-inverse. 
    The forward path uses encode and reverse path uses decode, such that decode(encode('A')) == 'A'. 

    Reference: Thimbleby, H., 2016. Human factors and missed solutions to Enigma design weaknesses. Cryptologia, 40(2), pp.177-202. 
    """                
    def __init__(self, 
                 rotor_names: list[str], 
                 reflector: EnhancedReflector, 
                 ring_settings: list[int], 
                 starting_positions: str, 
                 plugboard_pairs: list[str] | None = None,) -> None:
        """
        :param rotor_names: Refer to the EnigmaMachine in enigma.py.
        :param reflector: EnhancedReflector instance
        :param ring_settings: Refer to the EnigmaMachine in enigma.py.
        :param starting_positions: Refer to the EnigmaMachine in enigma.py.
        :param plugboard_pairs: Refer to the EnigmaMachine in enigma.py.
        :raises ValueError: If the reflector used is not an instance of the EnhancedReflector.
        """
        if not isinstance(reflector, EnhancedReflector):
            raise ValueError("""The EnhancedEnigmaMachine needs to use the EnhancedReflector, so that
                            letters can encrypt to themselves and that the reflector is not its own inverse.""")
        super().__init__(rotor_names, reflector, ring_settings, starting_positions, plugboard_pairs)        

    def decode_character(self, character:str) -> str:
        """
        Single letter decoding where the reflector will use its inverse mapping and 
        the relevant rotors step with each keypress. 
                
        :param character: A single letter of any case.
        :raises ValueError: if the character is not an alphabetical letter. 
        :return: The decoded uppercase letter. 
        """
        character = character.upper()
        if character not in ALPHABET:
            raise ValueError(f"The character {character} is not an alphabetical letter from A to Z.")
                            
        self._step_rotors()
                
        signal = self.plugboard.encode(character)

        for rotor in reversed(self.rotors):                 # reversed works through the rotor list from right to left
            signal = rotor.encode_right_to_left(signal)
                    
        signal = self.reflector.decode(signal)              # reflector using its inverse mapping

        for rotor in self.rotors:                           # rotors are stored left to right so no reversed needed
            signal = rotor.encode_left_to_right(signal)
        
        signal = self.plugboard.encode(signal)          # plugboard is self-inverse
                
        return signal
                    
    def decode_string(self, text: str) -> str:
        """
        Decode a string of characters, still advancing the relevant rotors with each keypress.
        Any non-alphabetical characters are ignored.

        :param text: Encrypted text of any case.
        :return: Decoded uppercase text.
        """
        return "".join(self.decode_character(c) for c in text.upper() if c in ALPHABET)     


                                                
                    







            


    

from enigma import (Reflector, EnigmaMachine, ALPHABET, ALPHA_TO_IDX)

class EnhancedReflector(Reflector):
    """ A non-standard Enigma reflector that takes in any permutation of 26-letters. 

    The standard Enigma Reflector was fixed-point-free so not letter could map to itself e.g. B couldn't map to B and 
    it had the property of involution meaning that any mapping was self-inverse so B-S and S-B. 
    These were both caused by the shared key/lamp wire in the Enigma Machine hardware (Thimbleby, 2016, p.189)

    If we remove these constraints, then encode and decode are separate operations. 

    Reference: Thimbleby, H., 2016. Human factors and missed solutions to Enigma design weaknesses. Cryptologia, 40(2), pp.177-202.

    """

    def __init__(self, name:str, wiring: str) -> Name:
        """
        :param name: The name fo the reflector e.g. 'A_enhanced'
        :param wiring: The 26-letter permutation string where each letter A-Z appears only one. 
        :raised ValueError: If the wiring does not conform to the 26-alphabetic-letter, no repetition wiring requirement. 
        """
        wiring = wiring.upper()
    
        if len(wiring) != 26:
            raise ValueError("Reflector wiring needs to be exactly 26 letters.")
        if not wiring.isalpha():
            raise ValueError("Reflector wiring can only contain alphabetic characters.")
        if len(set(wiring)) != 26:
            raise ValueError("The Reflector wiring can only contain each of the 26 alphabetic letters, once. ")
    
        # Set attributes directly for this sub-class to skip the stricter superclass logic that only checks for REFLECTOR_NAMES 'A', 'B' or 'C'
        self.name = name
        self.wiring = wiring 

        # decode inverse mapping, where wiring[i] = 'A' then inverse_wiring['A'] = ALPHABET[i]
        # not needed for the standard EnigmaMachine since it is its own self-inverse

        self.inverse_wiring: dict[str, str] = {char: ALPHABET[i] for i, char in enumerate(wiring)}

        def __repr(self) -> str:
            return f"EnhancedReflector(name='{self.name}', wiring='{self.wiring}')"
        
        def decode(self, character: str) -> str:
            """
            Leverage the inverse of the Reflector's wiring to decode a character. 
            :param character: A single letter of any case.
            :return: The inverse mapping for the letter.
            """
            return self.inverse_wiring[character.upper]
        
        class EnhancedEnigmaMachine(EnigmaMachine):
            """
            An updated EnigmaMachine that no longer has the reciprocal weakness of the standard machine (Thimbleby, 2016, p.177-202).

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
                         plugboard_pairs: list[str] | None = None,
            ) -> None:
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
                    Single letter decoding where the reflector will use its inverse mapping. 

                    :param character: A single letter of any case.
                    :raises ValueError: if the character is not an alphabetical letter. 
                    :return: The decoded uppercase letter. 
                    """
                    character = character.upper()
                    if character not in ALPHABET:
                        raise ValueError(f"The character {character} is not an alphabetical letter from A to Z.")
                    
                    self._step_rotors()

                    signal = self.plugboard.encode(character)

                    for rotor in reversed(self.rotors):              # right to left
                        signal = rotor.encode_right_to_left(signal)

                    signal = self.reflector.decode(signal)          




            


    

from enigma import EnigmaMachine, REFLECTOR_NAMES, ALPHABET

def solution_code_1():
    crib = 'SECRETS'
    code_text = 'DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ'

    for reflector in REFLECTOR_NAMES:
        
        enigma_machine = EnigmaMachine(
            rotor_names = ["Beta","Gamma","V"],
            reflector_name = reflector,
            ring_settings= [4, 2, 14],
            starting_positions = "MJM",
            plugboard_pairs = ["KI", "XN", "FL"],
            )
        output = enigma_machine.encode_string(code_text)

        if crib in output:
            print(f"Code 1, uses Reflector: {reflector}, Decoded text is: {output}")

def solution_code_2():
    crib = 'UNIVERSITY'
    code_text = 'CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH'

    for r_1 in ALPHABET:
        for r_2 in ALPHABET:
            for r_3 in ALPHABET:
                enigma_machine = EnigmaMachine(
                    rotor_names = ["Beta","I","III"],
                    reflector_name = "B",
                    ring_settings= [23, 2, 10],
                    starting_positions = r_1 + r_2 + r_3,
                    plugboard_pairs = ["VH", "PT", "ZG", "BJ", "EY", "FS"],
                    )
                output = enigma_machine.encode_string(code_text)
                if crib in output:
                    print(f"Code 2, uses rotor_positions: {r_1 + r_2 + r_3}, Decoded text is: {output}")
                    return      # stop the loop if crib is found to be in the output


if __name__ == "__main__":
    solution_code_1()
    solution_code_2()


        
        
    




from enigma import EnigmaMachine, REFLECTOR_NAMES

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

if __name__ == "__main__":
    solution_code_1()

        
        
    




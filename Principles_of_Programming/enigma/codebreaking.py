from enigma import EnigmaMachine, REFLECTOR_NAMES

crib = 'SECRETS'
code_text = 'DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ'

for reflector in REFLECTOR_NAMES:
    
    enigma_machine_1 = EnigmaMachine(
        rotor_names = ["Beta","Gamma","V"],
        reflector_name = reflector,
        ring_settings= [4, 2, 14],
        starting_positions = "MJM",
        plugboard_pairs = ["KI", "XN", "FL"],
        )
    output = enigma_machine_1.encode_string(code_text)
    if crib in output:
        print(reflector, output)


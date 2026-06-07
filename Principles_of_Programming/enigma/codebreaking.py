from enigma import EnigmaMachine, REFLECTOR_NAMES, ALPHABET
from itertools import permutations, product

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
            print(f"Code 1, uses Reflector: {reflector}, Decoded text: {output}")

def solution_code_2():
    crib = 'UNIVERSITY'
    code_text = 'CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH'
    crib_matches = []       # empty list to store any outputs that contain the crib

    for r_1, r_2, r_3 in product(ALPHABET, repeat=3):
        enigma_machine = EnigmaMachine(
            rotor_names = ["Beta","I","III"],
            reflector_name = "B",
            ring_settings= [23, 2, 10],
            starting_positions = r_1 + r_2 + r_3,
            plugboard_pairs = ["VH", "PT", "ZG", "BJ", "EY", "FS"],
            )
        
        output = enigma_machine.encode_string(code_text)

        if crib in output:
            crib_matches.append({"start_positions": r_1 + r_2 + r_3, "output": output})

    for match in crib_matches:
        print(f"Code 2 start_positions: {match['start_positions']}, Decoded text: {match['output']}")
    return crib_matches


def solution_code_3():
    crib = 'THOUSANDS'
    code_text = 'ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY'
    valid_rotor_names = ['Beta', 'Gamma', 'II', 'IV']
    valid_ring_settings = [2, 4, 6, 8, 20, 22, 24, 26]
    crib_matches = []       

    for rotors_used in permutations(valid_rotor_names, 3):
        for reflector_used in REFLECTOR_NAMES:
            for ring_settings_used in product(valid_ring_settings, repeat=3):
                enigma_machine = EnigmaMachine(
                    rotor_names = list(rotors_used),
                    reflector_name = reflector_used,
                    ring_settings= list(ring_settings_used),
                    starting_positions = "EMY",
                    plugboard_pairs = ["FH", "TS", "BE", "UQ", "KD", "AL"],
                    )
                output = enigma_machine.encode_string(code_text)
                if crib in output:
                    crib_matches.append({
                        "rotor_names": rotors_used, 
                        "reflector name": reflector_used, 
                        "ring_settings": ring_settings_used,
                        "output": output
                        })
    for match in crib_matches:
        print(f"""Code 3 rotors: {match['rotor_names']}, reflector: {match['reflector name']},
              ring settings: {match['ring_settings']}, Decoded text: {match['output']}""")
    return crib_matches

def solution_code_4():
        crib = 'TUTOR'
        code_text = 'SDNTVTPHRBNWTLMZTQKZGADDQYPFNHBPNHCQGBGMZPZLUAVGDQVYRBFYYEIXQWVTHXGNW' 
        crib_matches = [] 
        plugboard_pairs = 'WP RJ A? VF I? HN CG BS'.split()
        known_pairs = [p for p in plugboard_pairs if '?' not in p]
        used_letters = {c for p in plugboard_pairs for c in p if c != '?'}
        scenario_2_pool = set(ALPHABET) - used_letters 
        
        # Scenario 1: I and A are connected to each other:
        test_pairs = known_pairs + ['AI']
        enigma_machine = EnigmaMachine(
            rotor_names = ['V', 'III', 'IV'],
            reflector_name = 'A',
            ring_settings= [24, 12, 10],
            starting_positions = "EMY",
            plugboard_pairs = test_pairs,
            )
        output = enigma_machine.encode_string(code_text)
        if crib in output:
            crib_matches.append({"plugboard_pairs": test_pairs, "output": output})

        # Scenario 2: I and A are not connected to each other:
        for a_plug in scenario_2_pool:
            for i_plug in scenario_2_pool - {a_plug}:
                test_pairs = known_pairs + ['A' + a_plug] + ['I' + i_plug]
                enigma_machine = EnigmaMachine(
                    rotor_names = ['V', 'III', 'IV'],
                    reflector_name = 'A',
                    ring_settings= [24, 12, 10],
                    starting_positions = "SWU",
                    plugboard_pairs = test_pairs,
                    )
                output = enigma_machine.encode_string(code_text)
                if crib in output:
                    crib_matches.append({"plugboard_pairs": test_pairs, "output": output})
    
        for match in crib_matches:
            print(f"Code 4 plugboard pairs: {match['plugboard_pairs']}, Decoded text: {match['output']}")
        return crib_matches    
        


if __name__ == "__main__":
    solution_code_1()
    solution_code_2()
    solution_code_3()
    solution_code_4()


        
        
    




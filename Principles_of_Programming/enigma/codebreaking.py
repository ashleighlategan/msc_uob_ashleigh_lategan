from enigma import EnigmaMachine, Reflector, REFLECTOR_NAMES, ALPHABET, ROTOR_WIRING, ALPHA_TO_IDX
from itertools import permutations, product, combinations

def solution_code_1():
    crib = 'SECRETS'
    code_text = 'DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ'

    for reflector in REFLECTOR_NAMES:
        
        enigma_machine = EnigmaMachine(
            rotor_names = ["Beta","Gamma","V"],
            reflector = Reflector(reflector),
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
            reflector = Reflector("B"),
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
                    reflector = Reflector(reflector_used),
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
        reflector = Reflector('A'),
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
                reflector = Reflector('A'),
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
        
def solution_code_5():
    cribs = ['FACEBOOK', 'INSTAGRAM', 'TIKTOK', 'SNAPCHAT','YOUTUBE', 'WHATSAPP', 'LINKEDIN', 'PINTEREST', 'REDDIT']
    code_text = 'HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX' 
    crib_matches = [] 

    for reflector_name in REFLECTOR_NAMES:
        wiring = ROTOR_WIRING[reflector_name]
        pairs = [ (ALPHABET[i], wiring[i]) for i in range(26) if ALPHABET[i] < wiring[i]]
        checked_wires = set()                          # each reflector gets a new set

        for first_choice in combinations(pairs,2):
            for second_choice in combinations(pairs,2):
                if set(first_choice) & set(second_choice):      # skip if the pair was already chosen in first choice
                    continue
                for swap_1 in range(2):
                    (a1, a2) = first_choice[0]      # 1st pair e.g. ('C', 'M') where a1 = 'C' and a2 = 'M'
                    (b1, b2) = first_choice[1]      # 2nd pair e.g. ('F', 'P') where a1 = 'F' and a2 = 'P'
                    if swap_1 ==0:                  # becomes ('C','P'), ('F','M')
                        new_pairs_1 = [(a1, b2), (b1, a2)]
                    else:                           # becomes ('C','F'), ('M','P')
                        new_pairs_1 = [(a1, b1), (a2, b2)]

                    for swap_2 in range(2):
                        (c1, c2) = second_choice[0]      # 1st pair e.g. ('B', 'R') where a1 = 'B' and a2 = 'R'
                        (d1, d2) = second_choice[1]      # 2nd pair e.g. ('D', 'Z') where a1 = 'D' and a2 = 'Z'    
                        if swap_2 ==0:                  # becomes ('B','Z'), ('D','R)
                            new_pairs_2 = [(c1, d2), (d1, c2)]
                        else:                           # becomes ('B','D'), ('R','Z')
                            new_pairs_2 = [(c1, d1), (c2, d2)]
                                    
                        wiring_list = list(wiring)
                        for (x, y) in new_pairs_1 + new_pairs_2:        # unpack each of the swapped pairs and ensure they are saved in both directions so reflector is self-inverse
                            wiring_list[ALPHA_TO_IDX[x]] = y
                            wiring_list[ALPHA_TO_IDX[y]] = x
                                    
                        updated_wiring = "".join(wiring_list)
                        if updated_wiring in checked_wires:             # skip the already checked wires
                            continue
                        checked_wires.add(updated_wiring)               # record wiring as checked
                
                        enigma_machine = EnigmaMachine(
                            rotor_names = ['V', 'II', 'IV'],
                            reflector = Reflector(reflector_name, updated_wiring),
                            ring_settings= [6, 18, 7],
                            starting_positions = "AJL",
                            plugboard_pairs = ["UG", "IE", "PO", "NX", "WT"],
                        )
                        output = enigma_machine.encode_string(code_text)

                        for crib in cribs:
                            if crib in output:
                                crib_matches.append({
                                    'reflector': reflector_name,
                                    'new_pairs_1': new_pairs_1,
                                    'new_pairs_2': new_pairs_2,
                                    'output': output
                                })
    for match in crib_matches:
        print(f""" Code 5 Reflector: {match['reflector']}, output: {match['output']}
              new_pairs_1: {match['new_pairs_1']}
              new_pairs_2: {match['new_pairs_2']}""")
    return crib_matches

if __name__ == "__main__":
    solution_code_1()
    solution_code_2()
    solution_code_3()
    solution_code_4()
    solution_code_5()


        
        
    




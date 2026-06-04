
class PlugLead:
    def __init__(self, mapping):
        if len(mapping) != 2:
            raise ValueError ("A plug lead can only connect 2 characters")
        if mapping[0] == mapping[1]:
            raise ValueError("A plug lead cannot map a letter to itself.")
        if not mapping.isalpha():
            raise ValueError("Plug lead mappings are only for letters.")
        self.mapping = mapping.upper()
 
    def encode(self, character):
        character = character.upper()
        if character == self.mapping[0]:
            return self.mapping[1]
        elif character == self.mapping[1]:
            return self.mapping[0]
        else:
            return character


class Plugboard:
    pass


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

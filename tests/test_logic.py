# tests/test_logic.py


def test_nasa_mapping():
    mapping = {
        'Planet': 'Planète',
        'Moon': 'Lune',
        'Star': 'Étoile',
        'Dwarf Planet': 'Planète Externe',
    }

    test_cases = {
        'Planet': 'Planète',
        'Moon': 'Lune',
        'Star': 'Étoile',
        'Unknown': 'Unknown',
    }

    for input_type, expected in test_cases.items():
        result = mapping.get(input_type, input_type)
        assert result == expected, f"{input_type} -> {result}, attendu {expected}"


if __name__ == "__main__":
    test_nasa_mapping()

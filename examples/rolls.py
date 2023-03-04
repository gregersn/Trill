"""Example usage of Trill library."""
from typing import Dict
from trill import trill


def character_abilities():
    abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

    scores: Dict[str, int] = {}
    for name in abilities:
        result, error = trill('sum largest 3 4d6')
        assert not error
        assert result and isinstance(result[0], int)
        scores[name] = result[0]
    return scores


def main():
    for ability, score in character_abilities().items():
        print(f'{ability}: {score}')


if __name__ == '__main__':
    main()

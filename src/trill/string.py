"""String handling code."""
import re
from typing import List, Union

STRING_PATTERN = re.compile(r'(".*?")')

ALIGN_PATTERN = re.compile(r'(\|\||\|>|<\||<>)')

def pre_process(inp: str) -> str:
    strings: List[str] = STRING_PATTERN.findall(inp)
    for string in strings:
        if ALIGN_PATTERN.search(string):
            outstring = ALIGN_PATTERN.sub(r'"\1"', string)
            inp = inp.replace(string, outstring)

    return inp

def process_string(inp: str) -> Union[str, List[str], List[List[str]]]:

    string_parts: List[str] = []
    align_commands: List[str] = []

    start = 0
    string_iterator = enumerate(list(inp))
    for pos, char in string_iterator:
        if char in ['|', '>', '<']:
            if char == '|' and inp[pos + 1] in ['|', '>']:
                string_parts.append(inp[start:pos])
                align_commands.append(f"{char}{inp[pos + 1]}")
                next(string_iterator)
                start = pos + 2

            if char == '<' and inp[pos + 1] in ['|', '>']:
                string_parts.append(inp[start:pos])
                align_commands.append(f"{char}{inp[pos + 1]}")
                next(string_iterator)
                start = pos + 2

    string_parts.append(inp[start:])

    if not align_commands:
        return inp

    assert len(string_parts) == len(align_commands) + 1

    output: List[str] = []

    output.append(string_parts.pop())

    while align_commands:
        command = align_commands.pop()
        output.append(string_parts.pop())

        max_length = len(max(output, key=len))

        if command == '|>':
            output =  [f'{t:<{max_length}}' for t in output]

        if command == '<|':
            output =  [f'{t:>{max_length}}' for t in output]

        if command == '<>':
            output =  [f'{t:^{max_length}}' for t in output]

    return "\n".join(list(reversed(output)))

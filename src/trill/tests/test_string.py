from trill.string import process_string


def test_string_with_alignment():
    input_string = 'A  |>B|>C|>D'
    expected_output = "A  \nB  \nC  \nD  "

    output = process_string(input_string)

    assert len(output) == len(expected_output)

    assert output == expected_output

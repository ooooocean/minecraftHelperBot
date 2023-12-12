"""Unit tests for Discord bot"""

import pytest
import main


@pytest.mark.parametrize("test_input, expected_output",
                         [("1,1,1", True),
                          ("-1,-1,-1", True),
                          ("a,b,c", False)])
def test_check_string_format_coords(test_input, expected_output):
    """Checks for valid data inputs for coords regex function"""
    assert main.check_string_format_coords(test_input) == expected_output

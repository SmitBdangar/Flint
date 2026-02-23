import pytest
from flint.core.prompt import Prompt

def test_prompt_missing_key():
    p = Prompt("Hello {name}, my name is {bot}")
    with pytest.raises(ValueError):
        p.format(name="User")  # Missing 'bot'

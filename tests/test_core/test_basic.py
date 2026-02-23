import pytest
from flint.core.model import Model
from flint.core.prompt import Prompt
from flint.core.chain import Chain

def test_model_initialization():
    m = Model(name="llama3")
    assert m.name == "llama3"
    assert m.backend_name == "ollama"

def test_prompt_formatting():
    p = Prompt("Hello {name}!")
    assert p.format(name="World") == "Hello World!"

def test_chain_add():
    c = Chain()
    m = Model(name="llama3")
    p = Prompt("Tell me a joke")
    c.add(p).add(m)
    assert len(c.steps) == 2

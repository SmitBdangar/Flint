"""
Chain abstraction for Flint.
A simple way to string prompts and models together, avoiding LangChain bloat.
"""
from typing import List, Dict, Any, Union, Callable
import inspect


class Chain:
    """
    A simple pipeline for executing prompts against models and parsing outputs.
    """

    def __init__(self):
        self.steps: List[Any] = []

    def add(self, step: Any) -> "Chain":
        """
        Add a step to the chain.
        A step can be:
        1. A Prompt object
        2. A Model object (which will implicitly call its backend.generate)
        3. A callable (for custom processing, e.g. parsing output)
        """
        self.steps.append(step)
        return self

    async def run(self, **initial_kwargs) -> Any:
        """
        Execute the chain sequentially.
        """
        from flint.core.prompt import Prompt
        from flint.core.model import Model
        from flint.backends.ollama import OllamaBackend  # Import here to avoid circular logic initially

        current_state = initial_kwargs
        current_text = None

        for idx, step in enumerate(self.steps):
            if isinstance(step, Prompt):
                # Format prompt and set it as the current text
                current_text = step.format(**current_state)
            
            elif isinstance(step, Model):
                # Execute generation using the model
                if not current_text:
                    raise ValueError(f"Model step at index {idx} requires a preceding Prompt step to generate text.")
                
                # Temporary: hardcoded backend instantiation for v0.1 demo code logic
                # Ideally, this comes from a backend registry based on step.backend_name
                backend = OllamaBackend()
                
                # The generate call returns string text
                model_output = await backend.generate(prompt=current_text, model_name=step.name)
                
                current_text = model_output
                # Update state so subsequent prompts can use it if needed, often under 'text' or 'output'
                current_state['output'] = model_output
                
            elif callable(step):
                # Call a custom function
                # if the function is async, await it
                if current_text is not None:
                    # Pass the text to the callable
                    if inspect.iscoroutinefunction(step):
                        current_text = await step(current_text)
                    else:
                        current_text = step(current_text)
                    current_state['output'] = current_text
                else:
                    if inspect.iscoroutinefunction(step):
                        current_state = await step(current_state)
                    else:
                        current_state = step(current_state)

            else:
                raise TypeError(f"Unsupported chain step type: {type(step)}")

        return current_text

    def __repr__(self) -> str:
        return f"<Chain steps={len(self.steps)}>"

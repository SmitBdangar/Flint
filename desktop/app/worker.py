import asyncio
from PySide6.QtCore import QThread, Signal
from flint.backends import get_backend

class GenerationWorker(QThread):
    chunk_received = Signal(str)
    finished_generation = Signal()
    error_occurred = Signal(str)

    def __init__(self, prompt: str, model_name: str, backend_name: str):
        super().__init__()
        self.prompt = prompt
        self.model_name = model_name
        self.backend_name = backend_name

    def run(self):
        # We need a new event loop for this thread to run async backend calls
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            backend = get_backend(self.backend_name)
            loop.run_until_complete(self._generate_stream(backend))
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                pass
            loop.close()

    async def _generate_stream(self, backend):
        async for chunk in backend.generate_stream(self.prompt, self.model_name):
            if chunk:
                self.chunk_received.emit(chunk)

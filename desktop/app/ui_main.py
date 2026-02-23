import sys
import asyncio
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QTextEdit, QPushButton, QLabel, QSplitter,
    QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor

from flint.backends import get_all_backends
from app.worker import GenerationWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flint - Local AI Desktop")
        self.resize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #d4d4d4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #888888;
            }
        """)

        # Central Widget & Layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Splitter to separate sidebar and chat area
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        self._init_sidebar()
        self._init_chat_area()

        self.worker = None

        # Populate models on startup
        self.populate_models()

    def _init_sidebar(self):
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignTop)
        
        # Model Selection Label
        model_label = QLabel("Select Model")
        model_label.setFont(QFont("Arial", 12, QFont.Bold))
        sidebar_layout.addWidget(model_label)
        
        # Model Dropdown
        self.model_combo = QComboBox()
        sidebar_layout.addWidget(self.model_combo)

        # Refresh Button
        self.refresh_btn = QPushButton("Refresh Models")
        self.refresh_btn.clicked.connect(self.populate_models)
        sidebar_layout.addWidget(self.refresh_btn)
        
        # Stretch to push components to the top
        sidebar_layout.addStretch()

        self.splitter.addWidget(self.sidebar_widget)
        self.sidebar_widget.setMinimumWidth(250)
        self.sidebar_widget.setMaximumWidth(350)


    def _init_chat_area(self):
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout(self.chat_widget)
        
        # Chat History
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        # Add welcome message
        self.chat_history.append("<b>Flint Desktop</b><br>Welcome! Select a model and start chatting.<br><br>")
        chat_layout.addWidget(self.chat_history, stretch=1)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(100)
        self.input_box.setPlaceholderText("Type a message...")
        input_layout.addWidget(self.input_box)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedSize(80, 100)
        self.send_btn.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_btn)

        chat_layout.addLayout(input_layout)
        self.splitter.addWidget(self.chat_widget)

    def populate_models(self):
        """Asynchronously fetch models from all backends and populate the combo box."""
        self.model_combo.clear()
        self.model_combo.addItem("Loading models...", userData=None)
        self.model_combo.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.send_btn.setEnabled(False)

        # Fire and forget async call inside standard Qt GUI using a wrapper or loop
        # Since we are in the main UI thread, we can run a simple asyncio event loop locally just to fetch initial data, 
        # or use standard PySide QThread. For fetching lists, let's keep it simple with asyncio.run wrapper since list shouldn't be long blocking
        def fetch():
            backends = get_all_backends()
            async def _fetch():
                tasks = [b.list_models() for b in backends]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                all_models = []
                for res in results:
                    if isinstance(res, list):
                        all_models.extend(res)
                return all_models
            return asyncio.run(_fetch())
        
        # Normally should be threaded, but list_models is fast enough locally for v0.1
        try:
            models = fetch()
            self.model_combo.clear()
            if not models:
                self.model_combo.addItem("No models found", userData=None)
            else:
                for m in models:
                    self.model_combo.addItem(f"{m.name} ({m.backend_name})", userData=m)
        except Exception as e:
            self.model_combo.clear()
            self.model_combo.addItem("Error loading models", userData=None)
            print(f"Error fetching models: {e}")
        finally:
            self.model_combo.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            self.send_btn.setEnabled(True)

    def handle_send(self):
        model_data = self.model_combo.currentData()
        prompt = self.input_box.toPlainText().strip()

        if not model_data or not prompt:
            return

        # Disable inputs during generation
        self.input_box.clear()
        self.send_btn.setEnabled(False)
        
        # Append User Message
        self.chat_history.append(f"<b style='color: #4daafc;'>You:</b><br>{prompt}<br><br>")
        self.chat_history.append(f"<b style='color: #4daafc;'>{model_data.name} ({model_data.backend_name}):</b><br>")
        self.scrollToBottom()

        # Start QThread worker for generation
        self.worker = GenerationWorker(
            prompt=prompt,
            model_name=model_data.name,
            backend_name=model_data.backend_name
        )
        self.worker.chunk_received.connect(self.handle_chunk)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished_generation.connect(self.handle_finished)
        self.worker.start()

    def handle_chunk(self, chunk: str):
        # We append directly instead of line break
        text_cursor = self.chat_history.textCursor()
        text_cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(text_cursor)
        self.chat_history.insertPlainText(chunk)
        self.scrollToBottom()

    def handle_error(self, err: str):
        self.chat_history.append(f"<br><br><b style='color: red;'>Error: {err}</b><br>")
        self.scrollToBottom()

    def handle_finished(self):
        # End of assistant message formatting
        self.chat_history.append("<br><br>")
        self.scrollToBottom()
        self.send_btn.setEnabled(True)
        self.worker = None

    def scrollToBottom(self):
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

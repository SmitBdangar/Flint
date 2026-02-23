import sys
import asyncio
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QTextEdit, QPushButton, QLabel, QSplitter,
    QScrollArea, QFileDialog
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

        # Input Area Container
        input_container_layout = QVBoxLayout()
        
        # We store files attached for the current context
        self.attached_files = []
        
        # Input Text Box
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(100)
        self.input_box.setPlaceholderText("Type a message...")
        input_layout.addWidget(self.input_box)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedSize(80, 100)
        self.send_btn.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_btn)
        
        input_container_layout.addLayout(input_layout)
        
        # Tools bar underneath
        tools_layout = QHBoxLayout()
        self.attach_btn = QPushButton("📎 Attach File")
        self.attach_btn.setFixedSize(120, 30)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                font-size: 11px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        self.attach_btn.clicked.connect(self.handle_attach)
        tools_layout.addWidget(self.attach_btn)
        
        self.attached_files_label = QLabel()
        self.attached_files_label.setStyleSheet("font-size: 11px; color: #888888;")
        tools_layout.addWidget(self.attached_files_label)
        
        tools_layout.addStretch()
        input_container_layout.addLayout(tools_layout)

        chat_layout.addLayout(input_container_layout)
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

    def handle_attach(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Attach")
        if file_path:
            self.attached_files.append(file_path)
            # Update label
            filenames = [f.split("/")[-1] for f in self.attached_files]
            self.attached_files_label.setText("Attached: " + ", ".join(filenames))

    def handle_send(self):
        model_data = self.model_combo.currentData()
        prompt = self.input_box.toPlainText().strip()

        if not model_data or (not prompt and not self.attached_files):
            return

        # Disable inputs during generation
        self.input_box.clear()
        self.send_btn.setEnabled(False)
        self.attach_btn.setEnabled(False)
        
        # Build context from attached files
        context_block = ""
        if self.attached_files:
            context_block += "I am attaching the following files for context:\n\n"
            for file_path in self.attached_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    filename = file_path.split("/")[-1]
                    context_block += f"--- BEGIN FILE: {filename} ---\n{content}\n--- END FILE: {filename} ---\n\n"
                except Exception as e:
                    self.chat_history.append(f"<b style='color: red;'>Warning: Could not read file {file_path}: {e}</b><br>")
            
            # Append the actual user prompt
            if prompt:
                context_block += f"My prompt:\n{prompt}"
        else:
            context_block = prompt
            
        # Display the shortened version to user so chat isn't clustered with massive file text
        display_prompt = prompt
        if self.attached_files:
            filenames = [f.split("/")[-1] for f in self.attached_files]
            display_prompt = f"<i>[Attached: {', '.join(filenames)}]</i><br>" + display_prompt
        
        # Clear attached files state
        self.attached_files = []
        self.attached_files_label.setText("")
        
        # Append User Message
        self.chat_history.append(f"<b style='color: #4daafc;'>You:</b><br>{display_prompt}<br><br>")
        self.chat_history.append(f"<b style='color: #4daafc;'>{model_data.name} ({model_data.backend_name}):</b><br>")
        self.scrollToBottom()

        self.current_ai_message = ""

        # Start QThread worker for generation (send the full context_block to LLM)
        self.worker = GenerationWorker(
            prompt=context_block,
            model_name=model_data.name,
            backend_name=model_data.backend_name
        )
        self.worker.chunk_received.connect(self.handle_chunk)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished.connect(self.handle_finished)
        self.worker.start()

    def handle_chunk(self, chunk: str):
        self.current_ai_message += chunk
        # Update dynamically without rendering full markdown every token for performance
        # We replace the entire block of the current AI message
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(cursor)
        self.chat_history.insertPlainText(chunk)
        self.scrollToBottom()

    def handle_error(self, err: str):
        self.chat_history.append(f"<br><br><b style='color: red;'>Error: {err}</b><br>")
        self.scrollToBottom()

    def handle_finished(self):
        # When fully done, re-render the entire message nicely formatting code blocks
        import markdown
        
        # We need to find the start of the current message in the chat history
        # A simpler approach in v1.1 is just appending the rendered HTML
        # However, because we already inserted plaintext token-by-token, we 
        # need to replace the plaintext block. 
        # Let's use a simpler mechanism: we will clear the current raw text we just typed
        cursor = self.chat_history.textCursor()
        # Move back by the length of the string we appended
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(self.current_ai_message))
        cursor.removeSelectedText()
        
        # Convert markdown code blocks to HTML with syntax styles
        # Add basic styling to code blocks for Qt's rich text renderer
        html = markdown.markdown(self.current_ai_message, extensions=['fenced_code', 'tables'])
        
        # Inject custom CSS style into the block to make pre/code look good in Qt
        styled_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;">
            {html.replace('<pre>', '<pre style="background-color: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 5px; border: 1px solid #3d3d3d;">')
                 .replace('<code>', '<code style="background-color: #1e1e1e; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace;">')}
        </div>
        """
        
        self.chat_history.append(styled_html)
        self.chat_history.append("<br>")
        self.scrollToBottom()
        self.send_btn.setEnabled(True)
        self.attach_btn.setEnabled(True)
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def scrollToBottom(self):
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

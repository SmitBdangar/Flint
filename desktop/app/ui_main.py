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
                background-color: #212121; /* Main chat background */
            }
            QLabel {
                color: #ececec;
                font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif;
            }
            QComboBox {
                background-color: #2f2f2f;
                color: #ececec;
                border: 1px solid #424242;
                padding: 8px 12px;
                border-radius: 8px;
                font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ececec;
                margin-right: 12px;
            }
            QTextEdit {
                background-color: transparent;
                color: #ececec;
                border: none;
                font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
                line-height: 1.6;
            }
            /* The input box gets the rounded pill look */
            QTextEdit#InputBox {
                background-color: #2f2f2f;
                border: 1px solid #424242;
                border-radius: 20px;
                padding: 12px 20px;
            }
            QTextEdit#InputBox:focus {
                border: 1px solid #676767;
            }
            QPushButton {
                background-color: #ececec;
                color: #171717;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f9f9f9;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
            QPushButton:disabled {
                background-color: #424242;
                color: #676767;
            }
            /* The Chat History gets a specific style to hide borders */
            QTextEdit#ChatHistory {
                background-color: #212121;
                border: none;
            }
            QSplitter::handle {
                background-color: #171717; /* Sidebar handle */
            }
            QScrollBar:vertical {
                border: none;
                background: #212121;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #424242;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            #Sidebar {
                background-color: #171717;
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
        self.chat_widget.setStyleSheet("background-color: #212121;")
        chat_layout = QVBoxLayout(self.chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # --- Chat History Area (Scrollable & Centered) ---
        self.chat_history_container = QWidget()
        history_layout = QVBoxLayout(self.chat_history_container)
        history_layout.setAlignment(Qt.AlignHCenter)
        history_layout.setContentsMargins(0, 20, 0, 0)
        
        self.chat_history = QTextEdit()
        self.chat_history.setObjectName("ChatHistory")
        self.chat_history.setReadOnly(True)
        self.chat_history.setMaximumWidth(800)
        # Add welcome message
        self.chat_history.append("<div style='text-align: center; margin-top: 40px;'><h2>Flint Desktop</h2><p style='color: #ececec;'>Welcome! Select a model and start chatting.</p></div>")
        history_layout.addWidget(self.chat_history, stretch=1)
        
        chat_layout.addWidget(self.chat_history_container, stretch=1)

        # --- Input Area Container (Bottom & Centered) ---
        self.input_container_widget = QWidget()
        input_container_layout = QVBoxLayout(self.input_container_widget)
        input_container_layout.setAlignment(Qt.AlignHCenter)
        input_container_layout.setContentsMargins(0, 10, 0, 30)

        # A wrapper to constrain the width to 800px max
        self.input_wrapper = QWidget()
        self.input_wrapper.setMaximumWidth(800)
        input_wrapper_layout = QVBoxLayout(self.input_wrapper)
        input_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        # We store files attached for the current context
        self.attached_files = []
        
        # Tools bar above input
        tools_layout = QHBoxLayout()
        self.attach_btn = QPushButton("📎 Attach")
        self.attach_btn.setFixedSize(80, 30)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ececec;
                border: 1px solid #424242;
                border-radius: 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
            }
        """)
        self.attach_btn.clicked.connect(self.handle_attach)
        tools_layout.addWidget(self.attach_btn)
        
        self.attached_files_label = QLabel()
        self.attached_files_label.setStyleSheet("font-size: 11px; color: #ececec;")
        tools_layout.addWidget(self.attached_files_label)
        tools_layout.addStretch()
        input_wrapper_layout.addLayout(tools_layout)
        
        # Input Text Box & Send Button Row
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setObjectName("InputBox")
        self.input_box.setFixedHeight(80)
        self.input_box.setPlaceholderText("Message Flint...")
        input_layout.addWidget(self.input_box)

        # Send Button as a circular icon button
        self.send_btn = QPushButton("↑")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #ececec;
                color: #171717;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
                margin-left: 10px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #ffffff;
            }
        """)
        self.send_btn.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_btn, alignment=Qt.AlignBottom)
        
        input_wrapper_layout.addLayout(input_layout)
        
        # Disclaimer text
        disclaimer = QLabel("Flint can make mistakes. Consider verifying important information.")
        disclaimer.setStyleSheet("color: #676767; font-size: 11px; padding-top: 10px;")
        disclaimer.setAlignment(Qt.AlignCenter)
        input_wrapper_layout.addWidget(disclaimer)

        input_container_layout.addWidget(self.input_wrapper)
        chat_layout.addWidget(self.input_container_widget)
        
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
        
        # Append User Message (ChatGPT right-aligned rounded bubble style)
        self.chat_history.append(f"""
        <div style='display: flex; justify-content: flex-end; margin-bottom: 20px;'>
            <div style='background-color: #2f2f2f; color: #ececec; border-radius: 18px; padding: 10px 18px; max-width: 80%; text-align: left; font-size: 15px;'>
                {display_prompt}
            </div>
        </div>
        """)
        
        # Start AI Message (ChatGPT transparent background, left aligned)
        self.chat_history.append(f"""
        <div style='display: flex; justify-content: flex-start; margin-bottom: 5px; margin-top: 20px;'>
            <div style='color: #ececec; text-align: left; width: 100%; font-size: 15px;'>
                <b style='font-size: 16px;'>{model_data.name}</b><br><br>
        """)
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
        <div style="font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif; font-size: 14px; color: #f8fafc;">
            {html.replace('<pre>', '<pre style="background-color: #0f172a; color: #e2e8f0; padding: 12px; border-radius: 8px; border: 1px solid #334155; overflow-x: auto; margin-top: 8px; margin-bottom: 8px;">')
                 .replace('<code>', '<code style="background-color: #0f172a; padding: 2px 6px; border-radius: 4px; font-family: Consolas, Monaco, monospace; font-size: 13px; color: #cbd5e1;">')}
        </div>
        """
        
        self.chat_history.append(styled_html)
        # Close the AI message div block
        self.chat_history.append("</div></div><br>")
        self.scrollToBottom()
        self.send_btn.setEnabled(True)
        self.attach_btn.setEnabled(True)
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def scrollToBottom(self):
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

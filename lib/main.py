import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from docx import Document
from qa_model import QAModel  # Import the model logic

class QAApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Initialize the model
        self.qa_model = QAModel()
        self.context_loaded = False  # Track whether the context is loaded

    def initUI(self):
        # Main layout (horizontal to split left and right sides)
        main_layout = QHBoxLayout()

        # Left side layout
        left_layout = QVBoxLayout()

        # Title for the left side
        self.left_title = QLabel('Context and Question Input')
        self.left_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.left_title)

        # Text box to display context
        self.contextText = QTextEdit()
        self.contextText.setReadOnly(True)
        self.contextText.setText("Vui lòng tải file.")
        self.contextText.setStyleSheet('font-weight: bold;')
        left_layout.addWidget(self.contextText)

        # Label to display the answer
        self.answerLabel = QLabel('')
        left_layout.addWidget(self.answerLabel)

        # Horizontal layout for question input and buttons
        input_layout = QHBoxLayout()

        # Input field for question
        self.questionInput = QLineEdit(self)
        self.questionInput.setPlaceholderText('Enter your question here...')
        input_layout.addWidget(self.questionInput)

        # Connect the Enter key press to trigger get_answer
        self.questionInput.returnPressed.connect(self.get_answer)

        # Button to get the answer
        self.answerButton = QPushButton('Get Answer')
        self.answerButton.clicked.connect(self.get_answer)
        input_layout.addWidget(self.answerButton)

        # Button to load context from Word file
        self.loadButton = QPushButton('Load File')
        self.loadButton.clicked.connect(self.load_context)
        input_layout.addWidget(self.loadButton)

        # Add the horizontal layout to the left side layout
        left_layout.addLayout(input_layout)

        # Add the left layout to the main layout
        main_layout.addLayout(left_layout, stretch=2)  # Make left side take more space

        # Right side layout for history display
        right_layout = QVBoxLayout()

        # Title for the right side
        self.right_title = QLabel('Chat History')
        self.right_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.right_title)

        # Text box to display history of questions and answers
        self.historyText = QTextEdit()
        self.historyText.setReadOnly(True)
        self.historyText.setMinimumWidth(300)  # Set a minimum width for the history text area
        self.historyText.setMaximumWidth(400)  # Set a maximum width to prevent it from being too wide
        right_layout.addWidget(self.historyText)

        # Add the right layout to the main layout
        main_layout.addLayout(right_layout, stretch=3)  # Make right side wider

        # Apply custom styling
        self.apply_styles()

        # Set the main layout and window title
        self.setLayout(main_layout)
        self.setWindowTitle('QA System')
        self.setGeometry(300, 300, 1000, 400)  # Adjust the initial window size

    def apply_styles(self):
        # Stylesheet for rounded corners, height, width, bold text, and placeholder padding
        style = """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                
                /* border-bottom: 2px solid #5c7aff; */
            }
            QLineEdit {
                height: 40px;
                width: 300px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                padding-left: 10px;  /* Add padding to move placeholder text right */
            }
            QPushButton {
                height: 40px;
                width: 150px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                background-color: #5c7aff;
                color: white;
            }
            QPushButton:hover {
                background-color: #3b5aff;
            }
            QTextEdit {
                font-size: 16px;  /* Set the font size for the display area */
                font-family: Arial, sans-serif;  /* Set the font family for the display area */
                
            }
        """
        self.setStyleSheet(style)

    def load_context(self):
        # Load context from a Word document
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Word File", "", "Word Files (*.docx)")
        if file_path:
            context = self.load_context_from_docx(file_path)
            self.contextText.setText(context)
            self.contextText.setAlignment(Qt.AlignLeft)  # Reset alignment when context is loaded
            self.context_loaded = True
            self.enable_inputs(True)  # Enable input fields and buttons
        else:
            self.contextText.setText("Vui lòng tải file.")  # Reset message if no file is selected
            self.context_loaded = False
            self.enable_inputs(False)  # Disable input fields and buttons

    def load_context_from_docx(self, file_path):
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)

    def get_answer(self):
        if not self.context_loaded:
            self.show_warning("Please load a context file first.")
            return

        context = self.contextText.toPlainText()
        question = self.questionInput.text()

        if not question.strip():
            self.show_warning("Please enter a question.")
            return

        # Get the answer using the model
        answer = self.qa_model.get_answer(question, context)
        self.answerLabel.setText(f"Answer: {answer}")

        # Highlight the answer in the context
        highlighted_context = self.highlight_answer_in_context(context, answer)
        self.contextText.setHtml(highlighted_context)

        # Append question and answer to history with question on the left and answer on the right
        self.historyText.append(f"<b>Question:</b> {question}</div>")
        self.historyText.append(f"<b>Answer:</b> {answer}</div><div style='height: 10px;'></div>")  # Adjusted spacing

        # Clear the input field after getting the answer
        self.questionInput.clear()

    def highlight_answer_in_context(self, context, answer):
        # Escape HTML special characters in the context and answer
        context = context.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        answer = answer.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Replace the answer in the context with highlighted HTML
        highlighted_answer = f'<span style="background-color: yellow;">{answer}</span>'
        highlighted_context = context.replace(answer, highlighted_answer, 1)  # Replace only the first occurrence

        return highlighted_context

    def enable_inputs(self, enable):
        # Enable or disable the input fields and buttons
        self.questionInput.setEnabled(enable)
        self.answerButton.setEnabled(enable)

    def show_warning(self, message):
        # Show a warning message box
        QMessageBox.warning(self, "Warning", message)

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QAApp()
    ex.show()
    sys.exit(app.exec_())

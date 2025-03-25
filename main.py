import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt


class ITHelpdeskChatbot:
    def __init__(self):
        # Simple knowledge base for IT-related queries.
        self.knowledge_base = {
            "network": "For network issues, please try restarting your router and check your cable connections. If the problem persists, contact your network administrator.",
            "software": "For software installation queries, ensure you have the necessary permissions and follow the installation guide provided in our documentation.",
            "system": "For system configuration issues, please refer to the system configuration manual or reach out to IT support for further assistance.",
            "hello": "Hi! How can I help you today",
            "thank you": "You're welcome! I'm here if you need anything else."
        }

    def respond(self, query):
        # Convert query to lowercase for easier matching.
        query_lower = query.lower()
        if "network" in query_lower:
            return self.knowledge_base["network"]
        elif "software" in query_lower or "installation" in query_lower:
            return self.knowledge_base["software"]
        elif "system" in query_lower or "configuration" in query_lower:
            return self.knowledge_base["system"]
        elif "hello" in query_lower or "hi" in query_lower:
            return  self.knowledge_base["hello"]
        elif "thank you" in query_lower or "thanks" in query_lower:
            return self.knowledge_base["thank you"]
        else:
            # Default response if no keywords match.
            return "I'm sorry, I don't have an answer for that right now. Could you please provide more details?"


class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Intelligent IT Helpdesk Chatbot")
        self.setGeometry(100, 100, 600, 400)

        # Create an instance of the IT Helpdesk Chatbot.
        self.chatbot = ITHelpdeskChatbot()

        # Main layout for the window
        main_layout = QVBoxLayout(self)

        # Chat area (scrollable text area)
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)  # Make it read-only
        self.chat_area.setStyleSheet("""
            background-color: white;  # Set background to white
            font-family: Arial, sans-serif;
            font-size: 14px;
            color: black;  # Set text color to black
            border: 1px solid #ddd;  # Optional: add border for a subtle outline
        """)
        main_layout.addWidget(self.chat_area)

        # Bottom layout for user input and send button
        bottom_layout = QHBoxLayout()

        # Entry for user input
        self.entry_field = QLineEdit(self)
        self.entry_field.setPlaceholderText("Type your query...")
        self.entry_field.setStyleSheet("""
            padding: 10px;
            font-size: 14px;
            background-color: white;  # Set background to white
            color: black;  # Set text color to black
            border: 1px solid #ddd;  # Optional: add border for a subtle outline
        """)
        self.entry_field.returnPressed.connect(self.send_message)  # Trigger on pressing "Enter"
        bottom_layout.addWidget(self.entry_field)

        # Send button
        self.send_button = QPushButton("Send", self)
        self.send_button.setStyleSheet("""
            padding: 10px;
            font-size: 14px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
        """)
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)

        # Add bottom layout to the main layout
        main_layout.addLayout(bottom_layout)

    def send_message(self):
        user_message = self.entry_field.text().strip()
        if user_message:
            self.update_chat(f"You: {user_message}")
            response = self.chatbot.respond(user_message)
            self.update_chat(f"Chatbot: {response}")
            self.entry_field.clear()

    def update_chat(self, message):
        self.chat_area.append(message)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())


def main():
    app = QApplication(sys.argv)
    window = ChatbotGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import sys
import json
import hashlib
import os
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor

class UserDataManager:
    def __init__(self, filename="users.json"):
        self.filename = filename
        self.users = self._load_users()

    def _load_users(self):
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading user data: {e}")
            return {}

    def _save_users(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.users, f, indent=4)
        except IOError as e:
            print(f"Error saving user data: {e}")

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        if not username or not password:
            return False, "Username and password cannot be empty."
        if not username.isalnum():
             return False, "Username must be alphanumeric."
        if username in self.users:
            return False, "Username already exists."

        hashed_password = self._hash_password(password)
        self.users[username] = hashed_password
        self._save_users()
        return True, "Registration successful!"

    def check_login(self, username, password):
        if username not in self.users:
            return False

        hashed_password = self._hash_password(password)
        return self.users[username] == hashed_password

class ChatHistoryManager:
    def __init__(self, filename="chat_histories.json"):
        self.filename = filename
        self.histories = self._load_histories()

    def _load_histories(self):
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading chat history: {e}")
            return {}

    def _save_histories(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.histories, f, indent=4)
        except IOError as e:
            print(f"Error saving chat history: {e}")

    def get_user_history(self, username):
        return self.histories.get(username, [])

    def add_message_to_history(self, username, sender, message):
        if username not in self.histories:
            self.histories[username] = []

        timestamp = time.time()
        self.histories[username].append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message
        })
        self._save_histories()

class LoginWidget(QWidget):
    loginSuccess = Signal(str)
    switchToRegister = Signal()

    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("Login")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; margin-bottom: 10px;")
        layout.addWidget(self.error_label)
        self.error_label.hide()

        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            padding: 10px; font-size: 14px; background-color: #007BFF;
            color: white; border-radius: 5px; margin-top: 10px;
        """)
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        switch_button = QPushButton("Don't have an account? Register")
        switch_button.setStyleSheet("""
            padding: 8px; font-size: 12px; color: #007BFF;
            border: none; background-color: transparent;
        """)
        switch_button.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_button.clicked.connect(self.switchToRegister.emit)
        layout.addWidget(switch_button)

        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        self.username_input.setMaximumWidth(300)
        self.password_input.setMaximumWidth(300)


    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        self.error_label.hide()

        if not username or not password:
            self.show_error("Username and password are required.")
            return

        if self.user_manager.check_login(username, password):
            print(f"Login successful for user: {username}")
            self.loginSuccess.emit(username)
        else:
            self.show_error("Invalid username or password.")
            self.password_input.clear()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()

class RegisterWidget(QWidget):
    registrationComplete = Signal()
    switchToLogin = Signal()

    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("Register")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose Username (alphanumeric)")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet("padding: 10px; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.confirm_password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; margin-bottom: 10px;")
        layout.addWidget(self.error_label)
        self.error_label.hide()

        register_button = QPushButton("Register")
        register_button.setStyleSheet("""
            padding: 10px; font-size: 14px; background-color: #28A745;
            color: white; border-radius: 5px; margin-top: 10px;
        """)
        register_button.clicked.connect(self.handle_register)
        layout.addWidget(register_button)

        switch_button = QPushButton("Already have an account? Login")
        switch_button.setStyleSheet("""
             padding: 8px; font-size: 12px; color: #007BFF;
             border: none; background-color: transparent;
         """)
        switch_button.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_button.clicked.connect(self.switchToLogin.emit)
        layout.addWidget(switch_button)

        self.confirm_password_input.returnPressed.connect(self.handle_register)

        self.username_input.setMaximumWidth(300)
        self.password_input.setMaximumWidth(300)
        self.confirm_password_input.setMaximumWidth(300)

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        self.error_label.hide()

        if not username or not password or not confirm_password:
            self.show_error("All fields are required.")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match.")
            self.password_input.clear()
            self.confirm_password_input.clear()
            return

        success, message = self.user_manager.register_user(username, password)

        if success:
            QMessageBox.information(self, "Success", message)
            self.registrationComplete.emit()
            self.clear_fields()
            self.switchToLogin.emit()
        else:
            self.show_error(message)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.error_label.hide()

class ITHelpdeskChatbot:
    def __init__(self):
        self.knowledge_base = {
            "network": "For network issues, please try restarting your router and check your cable connections. If the problem persists, contact your network administrator.",
            "software": "For software installation queries, ensure you have the necessary permissions and follow the installation guide provided in our documentation.",
            "system": "For system configuration issues, please refer to the system configuration manual or reach out to IT support for further assistance.",
            "hello": "Hi there! How can I help you today?",
            "thank you": "You're welcome! I'm here if you need anything else."
        }

    def respond(self, query):
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
            return "I'm sorry, I don't have an answer for that right now. Could you please provide more details or ask about network, software, or system issues?"

class ChatbotWidget(QWidget):
    logoutRequest = Signal()

    def __init__(self, username, history_manager):
        super().__init__()
        self.username = username
        self.history_manager = history_manager
        self.chatbot = ITHelpdeskChatbot()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        top_bar_layout = QHBoxLayout()
        self.welcome_label = QLabel(f"Welcome, {self.username}!")
        self.welcome_label.setStyleSheet("font-size: 14px; margin-right: 10px;")
        top_bar_layout.addWidget(self.welcome_label)
        top_bar_layout.addStretch(1)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("""
            padding: 5px 10px; font-size: 12px; background-color: #DC3545;
            color: white; border-radius: 3px;
        """)
        self.logout_button.clicked.connect(self.logoutRequest.emit)
        top_bar_layout.addWidget(self.logout_button)
        main_layout.addLayout(top_bar_layout)


        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            background-color: white; font-family: Arial, sans-serif;
            font-size: 14px; color: black; border: 1px solid #ddd;
        """)
        main_layout.addWidget(self.chat_area)

        bottom_layout = QHBoxLayout()
        self.entry_field = QLineEdit(self)
        self.entry_field.setPlaceholderText("Type your query...")
        self.entry_field.setStyleSheet("""
            padding: 10px; font-size: 14px; background-color: white;
            color: black; border: 1px solid #ddd;
        """)
        self.entry_field.returnPressed.connect(self.send_message)
        bottom_layout.addWidget(self.entry_field)
        self.send_button = QPushButton("Send", self)
        self.send_button.setStyleSheet("""
            padding: 10px; font-size: 14px; background-color: #4CAF50;
            color: white; border-radius: 5px;
        """)
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)
        main_layout.addLayout(bottom_layout)

    def load_history(self):
        self.chat_area.clear()
        history = self.history_manager.get_user_history(self.username)
        if not history:
             self.display_message("Chatbot", self.chatbot.respond('hello'))
        else:
            for message_data in history:
                display_sender = "You" if message_data["sender"] == self.username else message_data["sender"]
                formatted_message = f"{display_sender}: {message_data['message']}"
                self.chat_area.append(formatted_message)

            self.scroll_to_bottom()

    def send_message(self):
        user_message = self.entry_field.text().strip()
        if user_message:
            self.display_message("You", user_message)
            self.history_manager.add_message_to_history(self.username, self.username, user_message)

            response = self.chatbot.respond(user_message)

            self.display_message("Chatbot", response)
            self.history_manager.add_message_to_history(self.username, "Chatbot", response)

            self.entry_field.clear()

    def display_message(self, sender, message):
        self.chat_area.append(f"{sender}: {message}")
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_area.setTextCursor(cursor)
        QApplication.processEvents()


    def reset_chat(self):
        self.chat_area.clear()
        self.display_message("Chatbot", self.chatbot.respond('hello'))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IT Helpdesk")
        self.setGeometry(100, 100, 650, 500)

        self.user_manager = UserDataManager()
        self.history_manager = ChatHistoryManager()

        self.stacked_widget = QStackedWidget()

        self.login_widget = LoginWidget(self.user_manager)
        self.register_widget = RegisterWidget(self.user_manager)
        self.chatbot_widget = None

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(0,0,0,0)

        self.login_widget.switchToRegister.connect(self.show_register_screen)
        self.login_widget.loginSuccess.connect(self.show_chat_screen)
        self.register_widget.switchToLogin.connect(self.show_login_screen)

        self.stacked_widget.setCurrentIndex(0)

    def show_login_screen(self):
        self.setWindowTitle("IT Helpdesk - Login")
        self.login_widget.clear_fields()
        self.stacked_widget.setCurrentIndex(0)

    def show_register_screen(self):
        self.setWindowTitle("IT Helpdesk - Register")
        self.register_widget.clear_fields()
        self.stacked_widget.setCurrentIndex(1)

    def show_chat_screen(self, username):
        self.setWindowTitle(f"IT Helpdesk - Logged in as {username}")

        chat_widget_index = 2

        current_chat_widget = self.stacked_widget.widget(chat_widget_index)
        if current_chat_widget:
             self.stacked_widget.removeWidget(current_chat_widget)
             current_chat_widget.deleteLater()

        self.chatbot_widget = ChatbotWidget(username, self.history_manager)
        self.chatbot_widget.logoutRequest.connect(self.handle_logout)

        self.stacked_widget.insertWidget(chat_widget_index, self.chatbot_widget)
        self.stacked_widget.setCurrentIndex(chat_widget_index)


    def handle_logout(self):
        print("User logged out.")
        self.setWindowTitle("IT Helpdesk - Login")
        self.login_widget.clear_fields()
        self.stacked_widget.setCurrentIndex(0)

        chat_widget = self.stacked_widget.widget(2)
        if chat_widget:
            self.stacked_widget.removeWidget(chat_widget)
            chat_widget.deleteLater()
            self.chatbot_widget = None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
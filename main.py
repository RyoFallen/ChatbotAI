import sys # Gerekli import
import os  # Gerekli import
import json
import hashlib
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
# QIcon importunu unutmayın
from PySide6.QtGui import QTextCursor, QIcon
from dotenv import load_dotenv # Import load_dotenv
import google.generativeai as genai # Import Gemini library

# ******** YENİ HELPER FONKSİYON *********
def get_base_path():
    """ Çalıştırılabilir dosyanın veya scriptin bulunduğu dizini alır """
    if getattr(sys, 'frozen', False):
        # PyInstaller ile paketlenmişse executable'ın yolunu kullan
        application_path = os.path.dirname(sys.executable)
    else:
        # Normal script olarak çalışıyorsa scriptin bulunduğu dizini kullan
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path
# ******** END HELPER FONKSİYON *********

# --- UserDataManager ---
class UserDataManager:
    def __init__(self, filename="users.json"):
        self.filename = os.path.join(get_base_path(), filename) # <--- Değiştirildi
        print(f"UserDataManager using file: {self.filename}") # Debug için eklendi
        self.users = self._load_users()

    def _load_users(self):
        if not os.path.exists(self.filename):
            print(f"User file not found: {self.filename}") # Debug
            return {}
        try:
            with open(self.filename, 'r', encoding='utf-8') as f: # encoding eklendi
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading user data from {self.filename}: {e}")
            return {}
        except Exception as e: # Genel hata yakalama
            print(f"Unexpected error loading user data: {e}")
            return {}

    def _save_users(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f: # encoding eklendi
                json.dump(self.users, f, indent=4, ensure_ascii=False) # ensure_ascii eklendi
        except IOError as e:
            print(f"Error saving user data to {self.filename}: {e}")
        except Exception as e: # Genel hata yakalama
            print(f"Unexpected error saving user data: {e}")


    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest() # encoding eklendi

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
        return self.users.get(username) == hashed_password # .get() ile daha güvenli


# --- ChatHistoryManager ---
class ChatHistoryManager:
    def __init__(self, filename="chat_histories.json"):
        self.filename = os.path.join(get_base_path(), filename) # <--- Değiştirildi
        print(f"ChatHistoryManager using file: {self.filename}") # Debug için eklendi
        self.histories = self._load_histories()

    def _load_histories(self):
        if not os.path.exists(self.filename):
            print(f"Chat history file not found: {self.filename}") # Debug
            return {}
        try:
            with open(self.filename, 'r', encoding='utf-8') as f: # encoding eklendi
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading chat history from {self.filename}: {e}")
            return {}
        except Exception as e: # Genel hata yakalama
            print(f"Unexpected error loading chat history: {e}")
            return {}


    def _save_histories(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f: # encoding eklendi
                json.dump(self.histories, f, indent=4, ensure_ascii=False) # ensure_ascii eklendi
        except IOError as e:
            print(f"Error saving chat history to {self.filename}: {e}")
        except Exception as e: # Genel hata yakalama
             print(f"Unexpected error saving chat history: {e}")


    def get_user_history(self, username):
        return self.histories.get(username, [])

    def add_message_to_history(self, username, sender, message):
        if username not in self.histories:
            self.histories[username] = []

        timestamp = time.time()
        # Store messages with roles (user/model) for potential future context
        role = "user" if sender == username else "model"
        self.histories[username].append({
            "timestamp": timestamp,
            "role": role, # Changed 'sender' to 'role'
            "parts": [message] # Changed 'message' to 'parts' list (Gemini format)
        })
        # Make saving more robust
        try:
             self._save_histories()
        except Exception as e:
             print(f"Failed to save history after adding message: {e}")


# --- LoginWidget (No code changes needed here) ---
class LoginWidget(QWidget):
    loginSuccess = Signal(str)
    switchToRegister = Signal()
    # ... (Keep existing LoginWidget code) ...
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


# --- RegisterWidget (No code changes needed here) ---
class RegisterWidget(QWidget):
    registrationComplete = Signal()
    switchToLogin = Signal()
    # ... (Keep existing RegisterWidget code) ...
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


# --- ITHelpdeskChatbot (No path changes needed inside, uses configured API key) ---
class ITHelpdeskChatbot:
    # ... (Keep existing ITHelpdeskChatbot code, including the corrected get_initial_greeting) ...
    def __init__(self):
        # --- Gemini Initialization ---
        try:
            # load_dotenv() call moved to main() to load before API key check
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                # This check is now primarily in main(), but keep a fallback
                raise ValueError("GOOGLE_API_KEY not found in environment variables during Chatbot init.")

            genai.configure(api_key=api_key)

            # Define generation configuration (optional, adjust as needed)
            self.generation_config = {
                "temperature": 0.7, # Controls randomness
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048, # Max length of response
            }

            # Define safety settings (optional, adjust as needed)
            self.safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]

            # Create the Gemini model instance
            self.model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", # Or "gemini-pro"
                                               generation_config=self.generation_config,
                                               safety_settings=self.safety_settings)

            # Define the persona/system instruction for the chatbot
            self.system_instruction = """
            You are 'Gemini Helpdesk', a friendly and helpful AI assistant.
            Your purpose is to assist users with common IT-related problems.
            Focus on topics like:
            - Network troubleshooting (WiFi issues, slow connection)
            - Software installation help (permissions, basic steps)
            - System configuration guidance (finding settings, basic setup)
            - Basic hardware issues (mouse/keyboard not working, printer connection)
            - Account issues (password resets - explain the process, don't ask for passwords)

            Keep your answers concise and easy to understand for non-technical users.
            If a problem is complex or requires administrative access, advise the user
            to contact the official IT support department or their administrator.
            Do not provide overly technical jargon unless necessary, and explain it if you do.
            Be polite and professional. Start the first conversation by introducing yourself briefly
            and asking how you can help.
            """

            # Start a chat session (better for context)
            # History items here are used to seed the chat, the actual history object
            # will contain google.generativeai.types.Content objects.
            self.chat = self.model.start_chat(history=[
                 {'role':'user', 'parts': ["Hello"]}, # Dummy user start to allow model intro
                 {'role':'model', 'parts': [self.system_instruction + "\nHi there! I'm Gemini Helpdesk. How can I assist you with your IT issue today?"]}
            ])
            print("Gemini model initialized successfully.")

        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.model = None
            self.chat = None
            raise RuntimeError(f"Failed to initialize Gemini: {e}") from e

    # ******** CORRECTED get_initial_greeting *********
    def get_initial_greeting(self):
        """Returns the initial greeting set up during initialization."""
        try:
            if self.chat and self.chat.history:
                if len(self.chat.history) > 1:
                    second_message = self.chat.history[1]
                    if second_message.role == 'model':
                        if second_message.parts:
                            full_intro = second_message.parts[0].text
                            greeting_start = full_intro.find("Hi there!")
                            if greeting_start != -1:
                                return full_intro[greeting_start:]
                            else:
                                print("Warning: Expected greeting 'Hi there!' not found in initial message.")
                                # Maybe return the full intro if specific greeting not found
                                # return full_intro
                        else:
                             print("Warning: Initial model message has no parts.")
                    else:
                        print(f"Warning: Expected second history item role to be 'model', but got '{second_message.role}'.")
                else:
                    print("Warning: Chat history has fewer than 2 items during initial greeting retrieval.")
        except Exception as e:
            print(f"Error retrieving initial greeting from history: {e}")

        print("Using fallback greeting.")
        return "Hello! How can I help you today?"
    # ******** END CORRECTED get_initial_greeting *********

    def respond(self, user_query): # Removed unused chat_history parameter
        """
        Generates a response using the Gemini model using the internal chat history.
        """
        if not self.chat:
             return "Sorry, the AI Chatbot is currently unavailable due to an initialization error."

        try:
            response = self.chat.send_message(user_query)

            if not response.parts:
                 block_reason = "Unknown"
                 if hasattr(response, 'candidates') and response.candidates:
                     candidate = response.candidates[0]
                     if hasattr(candidate, 'finish_reason') and candidate.finish_reason.name == 'SAFETY':
                         if hasattr(candidate, 'safety_ratings'):
                            safety_ratings = candidate.safety_ratings
                            blocked_categories = [rating.category for rating in safety_ratings if rating.probability.name not in ('NEGLIGIBLE', 'LOW')]
                            block_reason = f"Safety blockage ({', '.join(str(cat) for cat in blocked_categories)})"

                 print(f"Warning: Gemini response might be empty or blocked. Reason: {block_reason}")
                 if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                      print(f"Prompt Feedback Block Reason: {response.prompt_feedback.block_reason}")

                 return "I'm sorry, I cannot provide a response to that topic due to safety guidelines or other restrictions."

            return response.text # Extract the text content

        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            if "API key not valid" in str(e):
                return "Error: Invalid API Key. Please check your configuration."
            elif "Resource has been exhausted" in str(e):
                 return "Sorry, the service is currently busy (Quota Exceeded). Please try again later."
            return "Sorry, I encountered an error while trying to generate a response. Please try again."


# --- ChatbotWidget (load_history modified to disable sync) ---
class ChatbotWidget(QWidget):
    logoutRequest = Signal()
    # ... (Keep existing __init__, init_ui code) ...
    def __init__(self, username, history_manager):
        super().__init__()
        self.username = username
        self.history_manager = history_manager
        try:
            # Initialize the Gemini Chatbot
            self.chatbot = ITHelpdeskChatbot()
            self.chatbot_active = True
        except RuntimeError as e:
             # Handle initialization failure
             print(f"Chatbot initialization failed: {e}")
             self.chatbot = None # Ensure chatbot object doesn't exist or is None
             self.chatbot_active = False

        self.init_ui()
        self.load_history() # Load history after chatbot initialization attempt


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

        if not self.chatbot_active:
             self.entry_field.setPlaceholderText("Chatbot unavailable due to initialization error.")
             self.entry_field.setEnabled(False)
             self.send_button.setEnabled(False)

    # ******** load_history with sync disabled *********
    def load_history(self):
        self.chat_area.clear()
        history_data = self.history_manager.get_user_history(self.username)

        if self.chatbot_active and self.chatbot and not history_data:
             initial_greeting = self.chatbot.get_initial_greeting()
             self.display_message("Chatbot", initial_greeting)
             # self.history_manager.add_message_to_history(self.username, "Chatbot", initial_greeting)

        elif not self.chatbot_active:
             self.display_message("System", "Chatbot is currently unavailable. Please check console logs or contact support.")

        if history_data:
             for message_data in history_data:
                sender_role = message_data.get("role", "model")
                sender = "You" if sender_role == "user" else "Chatbot"
                message_parts = message_data.get("parts", [""])
                message = message_parts[0] if message_parts else ""
                formatted_message = f"{sender}: {message}"
                self.chat_area.append(formatted_message)

        # --- Sync Gemini's internal history ---
        # THIS SECTION IS COMMENTED OUT TO AVOID TYPE ERRORS
        # ... (Rest of commented out block remains commented) ...
        # print(f"Note: History sync from JSON to live chat context is disabled.")

        self.scroll_to_bottom()
    # ******** END load_history *********

    # ... (Keep existing send_message, display_message, scroll_to_bottom, reset_chat code) ...
    def send_message(self):
        if not self.chatbot_active or not self.chatbot:
             QMessageBox.warning(self, "Chatbot Unavailable",
                                 "The chatbot could not be initialized. Please check the setup (API key, libraries).")
             return

        user_message = self.entry_field.text().strip()
        if user_message:
            self.display_message("You", user_message)
            self.history_manager.add_message_to_history(self.username, self.username, user_message) # Uses new format internally

            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                response = self.chatbot.respond(user_message)
            finally:
                QApplication.restoreOverrideCursor()

            self.display_message("Chatbot", response)
            self.history_manager.add_message_to_history(self.username, "Chatbot", response) # Uses new format internally

            self.entry_field.clear()

    def display_message(self, sender, message):
        self.chat_area.append(f"{sender}: {message}")
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_area.setTextCursor(cursor)

    def reset_chat(self):
        self.chat_area.clear()
        if self.chatbot_active and self.chatbot:
            try:
                self.chatbot.chat = self.chatbot.model.start_chat(history=[
                    {'role':'user', 'parts': ["Hello"]},
                    {'role':'model', 'parts': [self.chatbot.system_instruction + "\nHi there! I'm Gemini Helpdesk. How can I assist you with your IT issue today?"]}
                ])
                initial_greeting = self.chatbot.get_initial_greeting()
                self.display_message("Chatbot", initial_greeting)
            except Exception as e:
                 print(f"Error resetting chat session: {e}")
                 self.display_message("System", "Error resetting chat. Please restart.")
        elif not self.chatbot_active:
             self.display_message("System", "Chatbot is currently unavailable.")


# --- MainWindow (No path changes needed here) ---
class MainWindow(QWidget):
    # ... (Keep existing MainWindow code) ...
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IT Helpdesk")
        self.setGeometry(100, 100, 650, 500)

        self.user_manager = UserDataManager()
        self.history_manager = ChatHistoryManager()

        self.stacked_widget = QStackedWidget()

        self.login_widget = LoginWidget(self.user_manager)
        self.register_widget = RegisterWidget(self.user_manager)
        self.chatbot_widget_instance = None

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
        self.cleanup_chatbot_widget()
        self.login_widget.clear_fields()
        self.stacked_widget.setCurrentIndex(0)

    def show_register_screen(self):
        self.setWindowTitle("IT Helpdesk - Register")
        self.cleanup_chatbot_widget()
        self.register_widget.clear_fields()
        self.stacked_widget.setCurrentIndex(1)

    def show_chat_screen(self, username):
        self.setWindowTitle(f"IT Helpdesk - Logged in as {username}")
        self.cleanup_chatbot_widget()

        try:
            self.chatbot_widget_instance = ChatbotWidget(username, self.history_manager)
            self.chatbot_widget_instance.logoutRequest.connect(self.handle_logout)
            self.stacked_widget.addWidget(self.chatbot_widget_instance)
            self.stacked_widget.setCurrentWidget(self.chatbot_widget_instance)
        except RuntimeError as e:
             QMessageBox.critical(self, "Chatbot Error",
                                  f"Failed to initialize the chatbot.\nPlease check your setup (API Key, .env file) and restart.\nError: {e}")
             self.show_login_screen()

    def handle_logout(self):
        print("User logged out.")
        self.show_login_screen()

    def cleanup_chatbot_widget(self):
         if self.chatbot_widget_instance:
             print("Cleaning up previous chatbot widget.")
             self.stacked_widget.removeWidget(self.chatbot_widget_instance)
             self.chatbot_widget_instance.deleteLater()
             self.chatbot_widget_instance = None


# --- Main execution ---
def main():
    app = QApplication(sys.argv)

    # ******** MODIFIED .env LOADING *********
    # Find .env relative to the executable/script directory
    base_dir = get_base_path()
    dotenv_path = os.path.join(base_dir, ".env")
    print(f"Attempting to load .env file from: {dotenv_path}") # Debug için eklendi
    loaded = load_dotenv(dotenv_path=dotenv_path)
    if not loaded:
        # Fallback to default search path if not found next to executable/script
        print(f"Warning: .env file not found at {dotenv_path}. Checking default locations.")
        loaded = load_dotenv()

    # Check for API key (after attempting to load .env)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
         msg_box = QMessageBox()
         msg_box.setIcon(QMessageBox.Icon.Critical)
         msg_box.setWindowTitle("Configuration Error")
         msg_box.setText("GOOGLE_API_KEY not found.")
         msg_box.setInformativeText(f"Please ensure you have a .env file either in the application directory ({base_dir}) or accessible via standard dotenv search paths, and that it contains your GOOGLE_API_KEY.\nExample:\nGOOGLE_API_KEY=\"YOUR_KEY_HERE\"")
         msg_box.exec()
         sys.exit(1) # Exit if key is missing
    # ******** END MODIFIED .env LOADING *********

    app.setApplicationName("IT Helpdesk Chatbot")

    # ******** MODIFIED ICON LOADING *********
    # Define icon path relative to executable/script
    icon_path = os.path.join(base_dir, "app_icon.png") # <-- İkon dosya adınızı buraya yazın
    print(f"Attempting to load icon from: {icon_path}") # Debug için eklendi

    window = MainWindow()

    # Set icon if file exists
    if os.path.exists(icon_path):
         app_icon = QIcon(icon_path)
         window.setWindowIcon(app_icon)
         # app.setWindowIcon(app_icon) # İsteğe bağlı: uygulama geneli ikon
    else:
         print(f"Warning: Icon file not found at '{icon_path}'. Using default icon.")
    # ******** END MODIFIED ICON LOADING *********

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
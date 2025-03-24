import tkinter as tk
from tkinter import scrolledtext


class ITHelpdeskChatbot:
    def __init__(self):
        # Simple knowledge base for IT-related queries.
        self.knowledge_base = {
            "network": "For network issues, please try restarting your router and check your cable connections. If the problem persists, contact your network administrator.",
            "software": "For software installation queries, ensure you have the necessary permissions and follow the installation guide provided in our documentation.",
            "system": "For system configuration issues, please refer to the system configuration manual or reach out to IT support for further assistance."
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
        else:
            # Default response if no keywords match.
            return "I'm sorry, I don't have an answer for that right now. Could you please provide more details?"


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent IT Helpdesk Chatbot")

        # Create a scrollable text area to display the conversation.
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=60, height=20)
        self.chat_area.pack(padx=10, pady=10)

        # Create an entry widget for user input.
        self.entry_field = tk.Entry(root, width=50)
        self.entry_field.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10))
        self.entry_field.bind("<Return>", self.send_message)

        # Create a send button.
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=(5, 10), pady=(0, 10))

        # Create an instance of the IT Helpdesk Chatbot.
        self.chatbot = ITHelpdeskChatbot()

    def send_message(self, event=None):
        user_message = self.entry_field.get().strip()
        if user_message:
            self.update_chat("You: " + user_message)
            response = self.chatbot.respond(user_message)
            self.update_chat("Chatbot: " + response)
            self.entry_field.delete(0, tk.END)

    def update_chat(self, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)


def main():
    root = tk.Tk()
    gui = ChatbotGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

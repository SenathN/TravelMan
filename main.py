"""
main.py — TravelMate Chatbot GUI
Tkinter-based chat interface with:
- Chat bubble style (user right, bot left)
- Emoji mood cues (surprised ❓, happy ✅, thinking 🤔)
- Learning mode when bot doesn't know answer
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import database
import engine

# Initialize database on startup
database.initialise_db()


class TravelMateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TravelMate ✈️ — Your AI Travel Assistant")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        # Learning mode state
        self.learning_mode = False
        self.pending_question = None

        self._setup_ui()

    def _setup_ui(self):
        """Build the GUI components."""
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_label = tk.Label(
            header,
            text="✈️ TravelMate — AI Travel Assistant",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap="word",
            font=("Arial", 11),
            bg="#ffffff",
            fg="#333333",
            padx=10,
            pady=10,
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure chat tags for styling
        self.chat_display.tag_config("user", justify="right", background="#e3f2fd", font=("Arial", 11))
        self.chat_display.tag_config("bot", justify="left", background="#f5f5f5", font=("Arial", 11))
        self.chat_display.tag_config("system", justify="center", foreground="#666666", font=("Arial", 9, "italic"))

        # Input frame
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(fill="x", padx=10, pady=10)

        # Input box
        self.input_box = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg="white",
            relief="solid",
            borderwidth=1
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", lambda e: self.send_message())

        # Send button
        send_button = tk.Button(
            input_frame,
            text="Send",
            font=("Arial", 11, "bold"),
            bg="#2c3e50",
            fg="white",
            relief="flat",
            width=8,
            command=self.send_message
        )
        send_button.pack(side="right", padx=(5, 0))

        # Action buttons frame
        actions_frame = tk.Frame(self.root, bg="#f0f0f0")
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Clear button
        clear_button = tk.Button(
            actions_frame,
            text="🗑️ Clear Chat",
            font=("Arial", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            command=self.clear_chat
        )
        clear_button.pack(side="left", padx=2)

        # Save button
        save_button = tk.Button(
            actions_frame,
            text="💾 Save Log",
            font=("Arial", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            command=self.save_chat
        )
        save_button.pack(side="left", padx=2)

        # Welcome message
        self._add_bot_message("Hello! I'm TravelMate ✈️\nI can help you find holiday packages, answer travel questions, and learn from you.\n\nHow can I assist you today?")

    def clear_chat(self):
        """Clear the chat display."""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.config(state="normal")
            self.chat_display.delete(1.0, "end")
            self.chat_display.config(state="disabled")
            self._add_bot_message("Chat cleared! How can I help you now?")

    def save_chat(self):
        """Save chat history to a text file."""
        content = self.chat_display.get(1.0, "end").strip()
        if not content:
            messagebox.showinfo("Save Chat", "Nothing to save!")
            return

        try:
            filename = "chat_log.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"--- TravelMate Chat Log ---\n\n{content}")
            messagebox.showinfo("Save Chat", f"Chat history saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Chat", f"Error saving chat: {e}")

    def _add_message(self, message, sender):
        """Add a message to the chat display with appropriate styling."""
        self.chat_display.config(state="normal")

        if sender == "user":
            self.chat_display.insert("end", f"You: {message}\n\n", "user")
        elif sender == "bot":
            self.chat_display.insert("end", f"TravelMate: {message}\n\n", "bot")
        elif sender == "system":
            self.chat_display.insert("end", f"{message}\n\n", "system")

        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

    def _add_user_message(self, message):
        """Add user message to chat."""
        self._add_message(message, "user")

    def _add_bot_message(self, message):
        """Add bot message to chat with emoji mood cue."""
        # Add appropriate emoji based on message content
        emoji = "✅"  # Default: happy/success
        if "?" in message or "I couldn't find" in message or "I don't know" in message:
            emoji = "❓"  # Surprised/questioning
        elif "learning" in message.lower() or "teach" in message.lower():
            emoji = "🤔"  # Thinking/learning

        self._add_message(f"{emoji} {message}", "bot")

    def _add_system_message(self, message):
        """Add system message to chat."""
        self._add_message(message, "system")

    def send_message(self):
        """Handle user message send."""
        user_input = self.input_box.get().strip()
        if not user_input:
            return

        self.input_box.delete(0, "end")
        self._add_user_message(user_input)

        # Process in thread to prevent GUI freeze
        threading.Thread(target=self._process_input, args=(user_input,), daemon=True).start()

    def _process_input(self, user_input):
        """Process user input through the engine."""
        if self.learning_mode:
            # User is teaching the bot
            self.root.after(0, lambda: self._handle_learning_response(user_input))
            return

        # Normal processing
        response = engine.process_user_input(user_input)

        if response:
            # Bot knows the answer
            self.root.after(0, lambda: self._add_bot_message(response))
        else:
            # Bot doesn't know — enter learning mode
            self.root.after(0, lambda: self._enter_learning_mode(user_input))

    def _enter_learning_mode(self, question):
        """Enter learning mode to ask user for the correct answer."""
        self.learning_mode = True
        self.pending_question = question
        self._add_system_message("🤔 I don't know the answer to that.")
        self._add_bot_message("Could you teach me? What should I say in response?")

    def _handle_learning_response(self, answer):
        """Save the learned response and exit learning mode."""
        if not answer.strip():
            self._add_bot_message("Okay, I won't learn that one.")
        else:
            engine.learn_response(self.pending_question, answer)
            self._add_bot_message(f"Thanks! I've learned that '{self.pending_question}' → '{answer}'")

        self.learning_mode = False
        self.pending_question = None


def main():
    """Run the TravelMate GUI application."""
    root = tk.Tk()
    app = TravelMateGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

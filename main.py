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
import time
import database
import engine

class TravelMateGUI:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide main window during splash

        # Show splash screen
        self.splash = tk.Toplevel()
        self.splash.title("Loading TravelMate...")
        self.splash.geometry("300x200")
        self.splash.configure(bg="#2c3e50")
        self.splash.overrideredirect(True)  # No window decorations
        
        # Center splash
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width // 2) - 150
        y = (screen_height // 2) - 100
        self.splash.geometry(f"300x200+{x}+{y}")

        tk.Label(
            self.splash, 
            text="✈️ TravelMate", 
            font=("Arial", 20, "bold"), 
            bg="#2c3e50", 
            fg="white"
        ).pack(expand=True)
        
        self.loading_label = tk.Label(
            self.splash, 
            text="Initializing AI Engine...", 
            font=("Arial", 10), 
            bg="#2c3e50", 
            fg="#bdc3c7"
        )
        self.loading_label.pack(pady=(0, 20))

        # Start initialization in background
        threading.Thread(target=self._initialize, daemon=True).start()

    def _initialize(self):
        """Heavy initialization happens here."""
        try:
            # 1. Initialize Database
            database.initialise_db()
            
            # 2. Initialize Engine (NLTK downloads, etc.)
            engine.initialize_engine()
            
            # small delay for smooth transition
            time.sleep(1) 
            
            # 3. Setup Main UI (on main thread)
            self.root.after(0, self._show_main_ui)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Initialization Error", str(e)))
            self.root.after(0, self.root.destroy)

    def _show_main_ui(self):
        """Transitions from splash to main UI."""
        self.splash.destroy()
        self.root.deiconify()  # Show main window
        
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
        cleaned = answer.strip()
        if not cleaned:
            self._add_bot_message("Okay, I won't learn that one.")
            self.learning_mode = False
            self.pending_question = None
            return

        # Reject or confirm obviously invalid answers (e.g., a single digit)
        if cleaned.isdigit() or len(cleaned) < 3:
            confirm = messagebox.askyesno("Confirm Learning",
                "The response you provided looks very short or numeric. Do you still want me to learn it?")
            if not confirm:
                # Keep learning mode active and ask for a clearer answer
                self._add_bot_message("Okay — please provide a clearer, human-readable answer for me to learn.")
                return

        # Save learned response
        try:
            engine.learn_response(self.pending_question, cleaned)
            self._add_bot_message(f"Thanks! I've learned that '{self.pending_question}' → '{cleaned}'")
        except Exception as e:
            self._add_bot_message(f"Sorry, I couldn't save that answer: {e}")

        self.learning_mode = False
        self.pending_question = None


if __name__ == "__main__":
    try:
        # Ensure database exists before launching GUI (safe idempotent call)
        try:
            database.initialise_db()
        except Exception:
            # Continue startup; GUI splash will also attempt initialization
            pass

        root = tk.Tk()
        app = TravelMateGUI(root)
        root.mainloop()
    except Exception as e:
        # Catch any errors during startup (e.g., import errors)
        import tkinter as tk
        from tkinter import messagebox
        import traceback
        
        # If root doesn't exist yet, create a hidden one for the messagebox
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            messagebox.showerror("Fatal Error", f"TravelMate failed to start:\n\n{str(e)}\n\n{traceback.format_exc()}")
            temp_root.destroy()
        except:
            # Fallback if even tkinter fails
            print(f"Fatal Error: {e}")
            traceback.print_exc()

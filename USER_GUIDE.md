# 📖 TravelMate User Guide & Training Materials

## 🚀 Getting Started
1. Ensure you have **Python 3.10+** installed.
2. Install dependencies: `pip install nltk`.
3. Run the application: `python main.py`.

## 💬 How to Interact
- **Greetings**: Say "Hello" or "Hi" to start.
- **Search Packages**: Ask things like "Show me Bali tours", "What do you have for Maldives?", or "I want to go to Europe".
- **General Info**: Ask about "Visa requirements", "Travel insurance", or "Best time to travel".
- **Booking**: Mention "booking" or "reserve" to get contact details.

## 🧠 Teaching the Bot
If the bot doesn't know an answer, it will enter **Learning Mode**:
1. It will ask: "Could you teach me? What should I say in response?"
2. Type your preferred answer and press Enter.
3. The bot will remember this for the next time anyone asks that same question!

## 🛠️ Tools
- **Clear Chat**: Clears the current window for a fresh start.
- **Save Log**: Saves your entire conversation to `chat_log.txt`.

## 📦 Running the Windows Executable (.exe)
If you are using the pre-built `TravelMate_v1.0.0.exe`:

### 🛡️ Handling Security Warnings
Since this is an unsigned application (not yet registered with Microsoft), Windows SmartScreen may show a warning: **"Windows protected your PC"** or **"Unknown Publisher"**.

To run the application:
1. Click on **"More info"** in the warning dialog.
2. Click **"Run anyway"**.

### 🛠️ Troubleshooting "Publisher Errors" or "File Not Found"
If the app is blocked or fails with a "Windows cannot find the file..." error:
- **Antivirus Interference**: This is the most common cause. Your Antivirus may have deleted the file immediately because it is an unsigned executable. 
    1. Check your Antivirus **Quarantine** or **Protection History**.
    2. Restore the file and select **"Allow"** or **"Exclude"**.
- **Unblock the File**:
    1. **Right-click** the `.exe` file and select **Properties**.
    2. At the bottom, check the **"Unblock"** box (if present) and click **Apply**.
- **Try the Folder Version**: If the single `.exe` continues to fail, use the **`onedir`** build mode (the version that comes in a folder). This version is much less likely to trigger Antivirus false positives.

---
*Happy Travels with TravelMate!*

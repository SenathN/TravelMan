# 🚀 Key Requirements for High Marks (A-Grade)

Based on the [instructions.md](file:///home/sinister/ESOFT/artificial-intelligence/CW2/TourMan/plan/instructions.md) and marking scheme, here are the critical points to focus on to secure maximum marks.

---

## 🛠️ Technical Implementation (50 Marks)

| Requirement | Current Status | How to Ace the Viva |
| :--- | :--- | :--- |
| **NLP Inference Engine** (22 pts) | ✅ **Robust NLP** in `engine.py`. | Explain how the bot handles **typos, grammar errors, and restructured sentences** using Lemmatization, Stop-word filtering, and Fuzzy Matching. |
| **Persistent Storage** (5 pts) | ✅ **SQLite** in `database.py`. | Show the two tables: `packages` (static facts) and `learned_responses` (dynamic facts). |
| **Machine Learning** (5 pts) | ✅ **Interactive Learning**. | Demonstrate the bot saying "I don't know" → Learning → Answering the same question correctly. |
| **NL Interface** (5 pts) | ✅ **Tkinter GUI**. | Highlight the chat-bubble style and the clear distinction between User and Bot messages. |
| **Quality & Mood** (6 pts) | ✅ **Emoji Moods**. | Point out the ❓, ✅, and 🤔 emojis that change based on whether the bot understands, succeeds, or is learning. |

---

## 📝 Documentation Requirements (20 Marks)
*This is where many students lose easy marks. Ensure your final PDF includes:*

- [ ] **P.E.A.S. Table**:
  - **Performance**: Accuracy of intent matching, speed of DB query.
  - **Environment**: User chat input, local database.
  - **Actuators**: Tkinter text display, SQLite write operations.
  - **Sensors**: Text input field, SQLite read operations.
- [ ] **State Transition Diagram**: Show the flow from `IDLE` → `PROCESSING` → `RESPONDING` (or `LEARNING`).
- [ ] **Algorithm Flowcharts**: Create a flowchart for the `process_user_input` logic in `engine.py`.
- [ ] **Research & Challenges**: Mention why you chose **NLTK** over simple regex (better handling of word variations).
- [ ] **Test Plan**: Include a table with "Input", "Expected Output", and "Actual Result" for at least 5 scenarios. Use the results from [test_robustness.py](file:///home/sinister/ESOFT/artificial-intelligence/CW2/TourMan/test_robustness.py) to prove the bot's intelligence.

---

## 🎤 Communication & Viva (20 Marks)
*Preparation is key.*

- **Slide Deck**: Keep it to 8-10 slides. Use screenshots of the GUI.
- **Live Demo**: 
  1. Ask about a package (e.g., "Show me Bali tours").
  2. Ask something it doesn't know.
  3. Teach it.
  4. Ask the same thing again to show it learned.
- **Code Snippets**: Be ready to show the `preprocess_input` function in `engine.py` if asked how NLP works.

---

## 🎨 Creativity (10 Marks)
- The **TravelMate** theme is strong. 
- The use of emojis (✈️, 📦, 📍, 💰) makes the output attractive and "showcase-ready".
- **Bonus Idea**: If you have time, add a "Clear Chat" button or a "Save Chat Log" feature to the GUI for extra "Professionalism" points.

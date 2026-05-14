# 🗺️ Chatbot Assignment — 1-Day Battle Plan

## Domain Choice: ✈️ Travel & Tourism Assistant
*Good scope, relatable, easy to demo, covers all marking criteria naturally.*

---

## Tech Stack (Simple & Portable)
- **Python 3** + `venv` (runs anywhere)
- **NLTK** — NLP (tokenizing, lemmatizing, intent matching)
- **SQLite3** — built-in to Python, zero extra install, covers the database requirement
- **Tkinter** — built-in GUI, no install needed
- **JSON** — intent/pattern knowledge base file

> No exotic libraries. Everything either ships with Python or installs in one line.

---

## 🕐 Hour-by-Hour Plan

### **Hour 1 — Setup + Skeleton**
```
1. Install Python, create venv
2. pip install nltk
3. Folder structure:
   travel_bot/
   ├── main.py          ← entry point + GUI
   ├── engine.py        ← inference engine (NLP logic)
   ├── database.py      ← SQLite helper
   ├── intents.json     ← static knowledge base
   └── chatbot.db       ← auto-created at runtime
```

### **Hour 2 — Knowledge Base (Database tier)**
- `intents.json` — hardcoded patterns: greetings, farewells, small talk
- `chatbot.db` (SQLite) — two tables:
  - `packages` — holiday packages (name, destination, price, duration)
  - `learned_responses` — bot's self-learned Q&A pairs (machine learning tier)

### **Hour 3 — Inference Engine (NLP tier)**
Three intelligence features (10 marks each):

| Feature | Implementation |
|---|---|
| **NLP / Lemmatization** | NLTK tokenize + lemmatize user input, match to intent patterns |
| **Searching** | Query SQLite for live package data based on keywords |
| **Learning** | If bot can't answer → ask user for correct answer → save to DB |

### **Hour 4 — GUI (Interface tier)**
- Tkinter chat window
- Chat bubble style (user right, bot left)
- Simple emoji/color cues for "mood" (surprised ❓, happy ✅, unknown 🤔)
- Input box + Send button

### **Hour 5 — Polish + Test**
- Test 10 conversations (test plan)
- Fix edge cases
- Add 5–6 travel packages to the DB seed data

### **Hour 6 — Documentation**
- PEAS table
- State transition diagram (simple text/draw.io)
- Flowchart of inference engine
- Screenshots

### **Hour 7 — Presentation Slides**
- 8–10 slides max
- Cover: problem, architecture, demo flow, PEAS, AI traits, conclusion

---

## 📦 What We'll Build — Feature Checklist

| Marking Criterion | What covers it | Marks |
|---|---|---|
| Suitable application | Travel & Tourism bot | 2 |
| NLP inference engine | NLTK lemmatize + intent matching | 22 |
| Persistent storage | SQLite packages + responses | 5 |
| Machine learning | Bot learns unknown answers | 5 |
| Text NL interface | Tkinter chat UI | 5 |
| Quality & appearance | Clean GUI, emoji cues | 6 |

---

## ✅ Ready to Start?

Tell me which step to tackle first. I'd recommend we go in order:

1. **"Let's set up the project and database"**
2. **"Build the inference engine"**
3. **"Build the GUI"**
4. **"Generate the documentation"**
5. **"Generate the slides"**

We can do each piece together — I'll write the code, explain what each part does as we go (so you understand it for the viva), and keep it clean enough to showcase.

**Say "Step 1 — let's go" and we'll start building.** 🚀
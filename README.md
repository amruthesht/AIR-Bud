# 🎓 AIR-Bud (Am I Ready?)

**Your AI-powered study companion** that transforms course syllabi into structured timelines, study plans, mock quizzes, and personalized readiness assessments.

Built for the **ASU AIR Spark Hackathon 2026**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Syllabus Upload** | Upload a PDF syllabus → AI extracts exams, quizzes, deadlines, topics |
| 📅 **Timeline & Calendar** | View course timeline, export to Google Calendar or iCal (.ics) |
| 🤖 **AI Study Companion** | Chat with AI in **Tutor Mode** (step-by-step teaching) or **Ask Mode** (direct answers) |
| 📝 **Notes & Assignments** | Upload lecture notes and assignments for AI-powered study support |
| ❓ **Mock Quizzes** | AI-generated quizzes with scoring and history tracking |
| 📊 **Readiness Assessment** | AI evaluates your preparedness for upcoming exams |
| 🗓️ **Study Plan Generator** | Personalized day-by-day study schedule |
| 🔑 **User Accounts** | Encrypted per-user storage with sign-up/sign-in |
| 🔗 **Bring Your Own Key** | Works with any OpenAI-compatible API (ASU, standard OpenAI, custom endpoints) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- An OpenAI-compatible API key (ASU OpenAI or standard OpenAI)

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd ASU_AIR_Spark_Hackathon

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy and edit env file
cp .env.example .env

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### First-Time Setup
1. **Create an account** — enter your name, username, and password
2. **Configure AI** — enter your API key in the sidebar (ASU default URL is pre-configured)
3. **Upload a syllabus** — upload any course PDF to get started

---

## 🏗️ Architecture

```
AIR-Bud/
├── app.py                          # Main entry point + onboarding
├── pages/                          # Streamlit pages (7 features)
│   ├── 01_Upload_Syllabus.py
│   ├── 02_Timeline_Calendar.py
│   ├── 03_Study_Companion.py
│   ├── 04_Notes_Assignments.py
│   ├── 05_Mock_Quiz.py
│   ├── 06_Readiness_Assessment.py
│   └── 07_Study_Plan.py
├── utils/                          # Backend logic
│   ├── auth.py                     # User auth + encrypted storage
│   ├── llm_client.py               # LLM API calls (BYOK)
│   ├── syllabus_parser.py          # PDF extraction + LLM parsing
│   ├── calendar_exporter.py        # iCal + Google Calendar
│   └── storage.py                  # Session state helpers
├── system_prompts/                 # LLM personality files
│   ├── base.txt                    # Core AIR-Bud personality
│   ├── tutor_mode.txt              # Tutor mode behavior
│   ├── ask_mode.txt                # Ask mode behavior
│   ├── syllabus_parser.txt         # PDF → structured data
│   ├── quiz_generator.txt          # Mock quiz creation
│   ├── study_plan.txt              # Study plan generation
│   └── readiness_assessment.txt    # Readiness evaluation
├── .github/workflows/              # CI/CD
│   ├── build-windows.yml           # PyInstaller Windows build
│   └── build-macos.yml             # PyInstaller macOS build (x64 + ARM)
└── requirements.txt                # Python dependencies
```

---

## 🖥️ Desktop Builds

GitHub Actions automatically builds standalone executables on every push:

- **Windows:** `.exe` — double-click to run
- **macOS:** Native binary (Intel + Apple Silicon)

Find the latest builds under [Releases](../../releases).

---

## 🔒 Data Storage

- User accounts are stored locally in `.userdata/`
- All user data is **encrypted** using Fernet symmetric encryption
- Each user has their own directory with:
  - Encrypted state file (syllabus, quizzes, notes, chat history)
  - Uploaded files (notes, assignments)
  - Profile information

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Python)
- **AI:** OpenAI-compatible LLM (GPT-4o-mini, GPT-4o, custom)
- **PDF Parsing:** PyPDF2 + LLM extraction
- **Calendar:** icalendar library + Google Calendar URL generation
- **Encryption:** cryptography (Fernet)
- **Build:** PyInstaller (via GitHub Actions)

---

## 📋 Evaluation Criteria Alignment

| Criteria | How AIR-Bud Delivers |
|---|---|
| **Use Case & Real-World Impact** | Addresses universal student pain point: exam anxiety and syllabus management |
| **Prototype Functionality** | 7 fully functional features in a working Streamlit app |
| **Innovation & Creativity** | Autonomous study infrastructure from a single PDF upload |
| **Cross-Functional Collaboration** | Blend of AI, UI/UX, and data engineering |
| **Pitch & Presentation** | Polished UI with clear value prop and live demo capability |

---

## 👥 Team

Built by Team AIR-Bud for the ASU AIR Spark Hackathon 2026.

---

## 📄 License

This project is for hackathon purposes. All rights reserved.

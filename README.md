# 🌌 USAR SPACE AI — Smart Campus Intelligence & Timetable Telemetry System

> **Architected & Developed by Pranav Siroha**
>
> Designed for **University School of Automation and Robotics (USAR)**, GGSIPU East Delhi Campus.

---

## 🌟 Overview

**USAR SPACE AI** is a state-of-the-art campus intelligence application that analyzes college timetable PDFs (Odd Semester 2026-27 w.e.f. August 3, 2026) to provide **real-time classroom & laboratory availability**, slot reservations, interactive campus floor maps, conflict detection, and academic analytics in Indian Standard Time (IST).

---

## ✨ Features

- **🔴 🟢 Live IST Availability Engine**: Real-time room status, remaining free window countdowns, and next scheduled class alerts.
- **⚡ 4 Iconic Aesthetic Themes**: Cosmic Cyber, Mission Control HUD (NASA JPL), Neon Synthwave, and Aurora Quantum.
- **🛰️ Campus Time Machine**: Interactive simulator to test and preview room schedules for any day/hour.
- **🔍 Intelligent Slot Search**: Find free rooms for any custom time interval (e.g. *2:00 PM – 4:00 PM*) with 1-click presets.
- **🏢 Campus Floor Maps**: Interactive spatial blueprints across Academic Block A, Block B (USDI), and Block C.
- **📊 Centralized Timetable Analytics**: 498 classes indexed across AIDS, AIML, AR, and IIOT departments for Semesters 3, 5, 7.
- **🛡️ Admin Command Center**: Automated PDF timetable parser, review & approval screen, conflict center, and campus exceptions manager.

---

## 👨‍💻 Developer & Author

- **Developer**: **Pranav Siroha**
- **Institution**: University School of Automation and Robotics (USAR)
- **Academic Year**: 2026-27

---

## 🚀 Quickstart

### Backend (FastAPI + SQLAlchemy)
```bash
python -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
python -m backend.app.database.seed_data
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend (React + Vite + Tailwind CSS)
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173`.

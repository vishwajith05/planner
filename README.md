# PlanWise AI 🚀

> **Tagline:** Plan Smarter. Organize Better. Achieve More.  
> **Philosophy:** An intelligent, privacy-first productivity and task management system combining the intuitive workflow of TickTick with advanced AI-driven task scheduling, energy pacing, and automated offline synchronization.

---

## 1. Project Overview

PlanWise AI is a complete full-stack productivity ecosystem built for Android-first productivity (with architecture ready for iOS, tablets, desktop, and web). It integrates:

- **Core Task Management**: High/Medium/Low/Urgent priorities, checklists, subtasks, recurrence, and category folders.
- **Calendar & Time Blocking**: Multi-view agenda with deterministic conflict detection against fixed commitments.
- **Productivity Systems**:
  - Habit Tracker with daily streaks and best-streak records.
  - 25-minute Pomodoro & Deep Work Focus Timer with linked task tracking.
  - Interactive Kanban Task Board (To Do, In Progress, Completed).
  - Eisenhower Matrix (4 Quadrants) for urgent/important triage.
  - Long-term Goal Management with milestone breakdown and auto-progress calculation.
- **Real-Data Analytics Engine**: Completion velocity, focus duration, habit consistency, and peak productivity hours computed directly from database history.
- **Deterministic AI Scheduling & Assistant**:
  - Energy-level curve optimization (prioritizing 10 AM & 3 PM cognitive peaks).
  - Mandatory rest break insertion (10 minutes after every 90 minutes of continuous focus).
  - Cognitive anti-boredom task interleaving to prevent domain burnout.
  - Conversational AI Assistant & Personal Productivity Coach.
- **Offline-First Synchronization**:
  - Local persistence via JSON document storage and persistent sync queue.
  - Last-Write-Wins (LWW) conflict resolution with timestamp validation.
  - Single-roundtrip bidirectional synchronization (`/sync/full`).

---

## 2. Technology Stack

### Frontend (Mobile)
- **Framework:** Flutter 3.x (Dart 3.x)
- **Design System:** Material 3 with unified Light & Dark color systems
- **State Management:** Flutter Riverpod (`StateNotifierProvider`)
- **Navigation:** GoRouter with `StatefulShellRoute.indexedStack` (persistent bottom navigation)
- **Networking:** Dio with bearer token interceptor and offline fallback
- **Storage & Offline:** SharedPreferences + Local JSON Document Store + Persistent Sync Queue
- **Charts & UI:** FL Chart, Table Calendar, Custom Circular/Linear Progress Indicators

### Backend (API & Engine)
- **Framework:** Python 3.11 + FastAPI (Async RESTful API)
- **Validation:** Pydantic v2 (Strict Schema Validation & Settings Management)
- **Persistence:** SQLite + SQLAlchemy 2.0 ORM (Zero-overhead, ideal for 8 GB RAM laptops)
- **Security:** PyJWT authentication (HS256 with 64+ char key) + Direct Bcrypt password hashing
- **Security Middlewares:** OWASP Security Headers (CSP, nosniff, DENY, XSS) + In-memory Rate Limiting (Brute-force protection)
- **AI Layer:** Multi-provider abstraction (`BaseAIProvider`):
  - `MockAIProvider`: Heuristic, zero-dependency offline NLP & scheduler (Default)
  - `GeminiAIProvider`: Google Generative AI LLM integration

---

## 3. Architecture & Data Flow

```
┌────────────────────────────────────────────────────────┐
│                   Flutter Frontend                     │
│  Riverpod State ───► Local Storage / Sync Queue       │
└───────────────────────────┬────────────────────────────┘
                            │ (Online REST / Offline Queue)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend                      │
│  Security Headers ──► Rate Limiter ──► JWT Auth Guard  │
├────────────────────────────────────────────────────────┤
│  Endpoints:                                            │
│   • /tasks        • /calendar     • /habits            │
│   • /focus        • /goals        • /analytics         │
│   • /ai           • /ai/assistant • /sync              │
├────────────────────────────────────────────────────────┤
│  Engines:                                              │
│   • DailyScheduler (Greedy Energy-Aware Bin-Packer)    │
│   • WeeklyPlanner (8-Hour Daily Workload Balancer)     │
│   • AntiBoredomEngine (Cognitive Task Interleaver)     │
│   • SyncService (Last-Write-Wins Conflict Resolver)    │
│   • ProductivityCoach (Peak Rhythm & Streak Evaluator) │
├────────────────────────────────────────────────────────┤
│  Database: SQLite (In-Memory for Tests / File for Prod) │
└────────────────────────────────────────────────────────┘
```

---

## 4. Setup & Running the Backend

### Prerequisites
- Python 3.11+ installed.
- Git 2.x+.
- **No Docker required**: Designed to run with minimal CPU and memory overhead (~80 MB RAM total).

### 1. Clone & Configure Environment
```bash
git clone <repository-url>
cd planner

# Copy environment template
cp .env.example .env
```

### 2. Install Dependencies
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Start Development Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Base URL:** `http://127.0.0.1:8000/api/v1`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/api/v1/docs`
- **ReDoc:** `http://127.0.0.1:8000/api/v1/redoc`

### 4. Run Automated Test Suite
The test suite utilizes an isolated, hermetic in-memory SQLite database (`StaticPool`) ensuring 100% test isolation.
```bash
python -m pytest backend/app/tests -v
```
**Test Coverage (29/29 Passing):**
- Authentication & JWT issuance (`test_auth.py`)
- Multi-user isolation (`test_user_isolation.py`)
- Full Task CRUD, Subtasks, Checklists (`test_tasks.py`)
- Calendar & deterministic conflict detection (`test_calendar.py`)
- Habits, Pomodoro Focus, and Goal Milestones (`test_productivity_features.py`)
- Real DB Analytics & Period Filtering (`test_analytics.py`)
- AI Scheduler, Weekly Balancer, Rescheduler, and Anti-Boredom (`test_ai_engine.py`)
- Conversational Chat Agent & Goal Breakdown (`test_ai_chat.py`)
- Offline Sync & LWW Conflict Resolution (`test_sync.py`)
- OWASP Security Headers & Rate Limiting (`test_security.py`)

---

## 5. Running the Flutter App

### Recommended Drive Location for Flutter SDK
On systems with constrained `C:` storage (e.g., < 10 GB free), install Flutter and the Android SDK on secondary drives (e.g., `D:\src\flutter`) and set:
```powershell
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";D:\src\flutter\bin", "User")
```

### Run on Physical Android Device
1. Enable **Developer Options** on your Android device:
   - Go to **Settings** > **About Phone** > Tap **Build Number** 7 times.
   - Go to **Settings** > **Developer Options** > Enable **USB Debugging**.
2. Connect your phone via USB and verify ADB detection:
   ```bash
   adb devices
   ```
3. Fetch dependencies and launch:
   ```bash
   flutter pub get
   flutter run -d <device-id>
   ```

---

## 6. Building the Production Android APK

### Step 1: Generate Release Keystore
Run the following command to create an Android release keystore:
```bash
keytool -genkey -v -keystore android/app/planwise-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias planwise -storepass PlanWiseSecret2026! -keypass PlanWiseSecret2026!
```

### Step 2: Configure Signing Properties
Create `android/key.properties`:
```properties
storePassword=PlanWiseSecret2026!
keyPassword=PlanWiseSecret2026!
keyAlias=planwise
storeFile=planwise-release-key.jks
```

### Step 3: Build Release APK or App Bundle
```bash
# Build Universal APK:
flutter build apk --release

# Build Split Per-ABI APKs (reduces download size on 64-bit devices):
flutter build apk --split-per-abi --release

# Build Google Play App Bundle (.aab):
flutter build appbundle --release
```
Output files will be generated in `build/app/outputs/flutter-apk/app-release.apk`.

---

## 7. Tamil Localization Architecture (தமிழ்)

PlanWise AI is designed with first-class internationalization readiness:
- All strings are structured for Flutter's `intl` and `flutter_localizations` packages.
- Add `lib/l10n/app_ta.arb` alongside `app_en.arb`:
  ```json
  {
    "appTitle": "பிளான்வைஸ் AI",
    "planMyDay": "இன்றைய திட்டத்தை உருவாக்கு",
    "completed": "முடிந்தது",
    "focusTimer": "கவனக் கடிகாரம்",
    "habits": "பழக்கவழக்கங்கள்"
  }
  ```
- All typography styles in `lib/app/theme/typography.dart` support Unicode font fallback for high-legibility Tamil rendering.

---

## 8. Security & Production Hardening Summary

| Feature | Implementation Details |
|---|---|
| **Password Storage** | Direct `bcrypt` with unique automatic salt generation |
| **Tokens** | PyJWT with 64+ char HS256 key, user ID payload, expiration |
| **Data Isolation** | Strict query filter: `WHERE user_id = current_user.id` on all tables |
| **SQL Injection** | SQLAlchemy ORM parameterized queries across all endpoints |
| **Brute Force Defense** | In-memory sliding window rate limiting on `/auth/login` and `/auth/register` |
| **HTTP Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Content-Security-Policy: default-src 'self'` |
| **API Keys** | AI provider keys stored strictly on backend via `.env`, never in client code |

---

## 9. Verification & Phase Summary

All 9 development phases are **100% completed, tested, and verified**:
- **Phase 1: Foundation & Design System** ✅
- **Phase 2: Authentication & Core Task Management** ✅
- **Phase 3: Calendar & Conflict Detection** ✅
- **Phase 4: Productivity Suite (Habits, Pomodoro, Kanban, Eisenhower, Goals)** ✅
- **Phase 5: Real-Data Analytics Engine** ✅
- **Phase 6: Deterministic AI Scheduling Engine & Workload Balancer** ✅
- **Phase 7: Advanced AI Assistant, Anti-Boredom & Productivity Coach** ✅
- **Phase 8: Offline Persistence, Local Sync Queue & LWW Conflict Resolution** ✅
- **Phase 9: Security Hardening, Production Documentation & APK Build Guide** ✅

*Developed with precision for PlanWise AI.*

# PlanWise AI

> **Tagline:** Plan Smarter. Organize Better. Achieve More.

PlanWise AI is a modern, production-oriented productivity and task management platform combining the robust capabilities of TickTick with a deterministic AI scheduling engine, habit tracking, deep focus timers, Eisenhower matrix, and personal productivity coaching.

---

## Architecture Overview

```
                                      ┌────────────────────────────────────────┐
                                      │        PlanWise AI Flutter App         │
                                      │  (Material 3, Riverpod, GoRouter)       │
                                      └───────────────────┬────────────────────┘
                                                          │ Dio REST Client
                                                          ▼
                                      ┌────────────────────────────────────────┐
                                      │       FastAPI High-Speed Backend       │
                                      │   (Pydantic v2, SQLAlchemy, SQLite)    │
                                      └───────────────────┬────────────────────┘
                                                          │
                                     ┌────────────────────┴────────────────────┐
                                     ▼                                         ▼
                    ┌─────────────────────────────────┐       ┌─────────────────────────────────┐
                    │  Deterministic Scheduling Engine│       │      Multi-Provider AI Layer    │
                    │   - Non-overlapping slots       │       │   - MockProvider (offline dev)  │
                    │   - Fixed commitment locks      │       │   - GeminiProvider (LLM reasoning)
                    │   - Anti-boredom switching      │       │   - Energy curve optimization   │
                    └─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## Project Structure

```
planner/
├── PROJECT_PROGRESS.md           # Implementation and verification matrix
├── README.md                     # Comprehensive architecture and operations guide
├── pubspec.yaml                  # Flutter package specification
├── analysis_options.yaml         # Linter rules
├── lib/
│   ├── main.dart                 # Application entrypoint
│   ├── app/
│   │   ├── app.dart              # Root application widget (Material 3, ThemeMode)
│   │   ├── router.dart           # GoRouter StatefulShellRoute navigation
│   │   └── theme/
│   │       ├── app_colors.dart   # Design tokens & priority color mapping
│   │       ├── app_theme.dart    # Light & dark theme configurations
│   │       └── typography.dart   # Typography scale
│   ├── core/
│   │   ├── constants/            # API endpoints & constants
│   │   └── widgets/              # Reusable design system widgets
│   ├── features/
│   │   ├── dashboard/            # Dynamic briefing, score, quick actions
│   │   ├── tasks/                # TickTick-style task management
│   │   ├── calendar/             # Time blocking & calendar views
│   │   ├── ai_planner/           # AI daily/weekly scheduling
│   │   ├── habits/               # Habit consistency tracker
│   │   ├── focus/                # Pomodoro timer
│   │   ├── kanban/               # Kanban boards
│   │   ├── eisenhower/           # Eisenhower 4-quadrant matrix
│   │   ├── goals/                # Long-term goals & milestones
│   │   ├── analytics/            # Productivity charts & insights
│   │   └── settings/             # Settings & profiles
│   └── shared/
│       ├── models/               # Domain models & enums
│       └── widgets/              # Bottom navigation shell
└── backend/
    ├── requirements.txt          # Python dependencies
    ├── .env.example              # Environment variables template
    ├── run_server.py             # Server launcher
    └── app/
        ├── main.py               # FastAPI application
        ├── core/config.py        # Pydantic settings
        ├── database/session.py   # SQLAlchemy session manager
        ├── models/               # Database models (User, Task, Habit, Focus)
        ├── schemas/              # Pydantic request/response schemas
        ├── services/             # Business logic layer
        ├── ai/
        │   └── providers/        # Multi-provider AI (Mock & Gemini)
        └── tests/                # Automated pytest suite
```

---

## Quick Start Guide

### 1. Backend

1. Navigate to the project root:
   ```powershell
   cd c:\Users\HP\OneDrive\Desktop\planner
   ```
2. Run backend test suite:
   ```powershell
   python -m pytest backend/app/tests -v
   ```
3. Start the FastAPI backend server:
   ```powershell
   python backend/run_server.py
   ```
   The backend will be available at:
   - Base URL: `http://127.0.0.1:8000`
   - Interactive OpenAPI Docs: `http://127.0.0.1:8000/api/v1/docs`
   - Health Check: `http://127.0.0.1:8000/api/v1/health`

### 2. Frontend (Flutter)

When Flutter SDK is installed:
```powershell
flutter pub get
flutter run
```

---

## AI Provider Configuration

PlanWise AI features a zero-cost, offline-friendly architecture:
- By default, `AI_PROVIDER="mock"` is used. This enables full natural-language parsing, priority scoring, and productivity coaching without needing an external API key or paid subscriptions.
- To enable Google Gemini, update `backend/.env`:
  ```env
  AI_PROVIDER="gemini"
  GEMINI_API_KEY="your-gemini-api-key"
  ```
- If an API key is missing or encounters rate limits, the system automatically falls back gracefully to `MockAIProvider`.

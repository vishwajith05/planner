# PlanWise AI: Flutter to Web Conversion Plan & Migration Architecture

**Tagline:** Plan Smarter. Organize Better. Achieve More.  
**Target Platform:** Desktop, Laptop, Tablet, Mobile Browsers (Android & iOS) + Installable PWA.  
**Technology Shift:** Flutter / Dart ➔ React.js / TypeScript / Vite / Tailwind CSS / Zustand / TanStack Query.  
**Backend:** FastAPI / Python 3.11 / SQLite + Firebase Web SDK compatibility.

---

## 1. Existing Project Inventory (Flutter & Backend)

### A. Existing Flutter Codebase (`lib/`)
The Flutter codebase contains 32 Dart files structured according to Clean Architecture:

| Directory | Files / Components | Purpose in Flutter |
|---|---|---|
| `lib/app/` | `app.dart`, `router.dart`, `theme/` (`app_colors.dart`, `app_theme.dart`, `typography.dart`) | App bootstrap, GoRouter shell navigation (5 bottom nav tabs + 7 sub-routes), Material 3 Dark/Light theming |
| `lib/core/` | `constants/api_constants.dart`, `network/api_client.dart`, `storage/local_storage.dart`, `sync/` (`sync_queue.dart`, `sync_service.dart`), `widgets/` (`app_button.dart`, `app_card.dart`, `empty_state.dart`, `priority_badge.dart`) | Dio HTTP client with JWT interceptor, SharedPreferences JSON store, offline persistent mutation queue, reusable UI atoms |
| `lib/features/dashboard/` | `dashboard_screen.dart`, `productivity_score_card.dart`, `stats_overview_row.dart`, `quick_actions_card.dart`, `today_tasks_preview.dart` | Morning greeting, daily overview metrics, quick action launcher, today's schedule preview |
| `lib/features/tasks/` | `task_model.dart`, `task_repository.dart`, `task_provider.dart`, `tasks_screen.dart`, `create_task_sheet.dart` | Riverpod state, offline-first fallback, search, priority/category chips, subtasks counter, bottom sheet modal |
| `lib/features/calendar/` | `calendar_screen.dart` | Day/Week/Agenda views, weekly date strip, conflict detection banner, fixed-commitment lock badges |
| `lib/features/ai_planner/` | `ai_planner_screen.dart` | Tabbed UI: 1) Daily AI schedule with energy pacing, 2) Weekly 8h workload balancer, 3) AI Assistant chat |
| `lib/features/habits/` | `habits_screen.dart` | Daily/weekly habit checklist, streak count badge, all-time best streak, progress bar |
| `lib/features/focus/` | `focus_screen.dart` | 25m Pomodoro / 5m break / 15m long break circular countdown timer, linked task selector |
| `lib/features/kanban/` | `kanban_screen.dart` | To Do, In Progress, Completed columns with interactive card movement |
| `lib/features/eisenhower/` | `eisenhower_screen.dart` | 4-Quadrant Eisenhower Matrix (Urgent & Important triage grid) |
| `lib/features/goals/` | `goals_screen.dart` | Long-term goals, milestone check-offs, dynamic progress % recalculation |
| `lib/features/analytics/` | `analytics_screen.dart` | Period filters (Today, This Week, This Month), category breakdown bars, peak energy detection |
| `lib/features/settings/` | `settings_screen.dart` | Profile info, theme mode toggle, notification preferences, account deletion |
| `lib/shared/` | `models/priority.dart`, `widgets/bottom_nav_shell.dart` | Shared priority enum, persistent bottom navigation bar |

### B. Existing Reusable Backend Codebase (`backend/app/`)
The FastAPI backend contains 45 Python modules and 29 automated tests. **100% of this backend logic will be preserved and reused directly:**

- **Models (`models/`)**: `User`, `Task`, `Category`, `CalendarEvent`, `Habit`, `HabitCompletion`, `FocusSession`, `Goal`, `Milestone`.
- **Services (`services/`)**: `AuthService`, `TaskService`, `CalendarService` (with conflict detection), `HabitService` (streak engine), `FocusService`, `GoalService` (auto-progress), `AnalyticsService` (real DB metrics), `SyncService` (LWW conflict resolution), `AIService`.
- **AI Engines (`ai/`)**: `DailyScheduler` (greedy energy-aware bin-packer), `WeeklyPlanner` (8h daily cap balancer), `Rescheduler` (overdue slot detector), `AntiBoredomEngine` (cognitive task interleaving), `ChatAgent`, `ProductivityCoach`.
- **Security (`core/`)**: Direct `bcrypt` password hashing, PyJWT tokens, OWASP Security Headers Middleware, In-Memory Sliding Window Rate Limiter.
- **REST Endpoints (`api/v1/endpoints/`)**: `/auth`, `/tasks`, `/calendar`, `/habits`, `/focus`, `/goals`, `/analytics`, `/ai`, `/ai/assistant`, `/sync`.
- **Automated Tests (`tests/`)**: 29/29 pytest tests passing with hermetic in-memory SQLite isolation.

---

## 2. Flutter-to-Web Technology Mapping

| Architectural Layer | Existing Flutter Technology | New Web Technology | Migration Strategy & Web Benefits |
|---|---|---|---|
| **Core Framework** | Flutter 3.x / Dart 3.x | **React.js 18+ / TypeScript / Vite** | Instant HMR, zero mobile compilation overhead, runs universally in all desktop and mobile browsers |
| **Styling & Design System** | Material 3 (`app_theme.dart`) | **Tailwind CSS + shadcn/ui** | Clean, dark/light theme classes (`dark:`), CSS variables matching PlanWise violet (`#8B5CF6`) |
| **Navigation & Routing** | GoRouter (`StatefulShellRoute`) | **React Router DOM v6** | Nested routes with `<AppLayout>` sidebar on desktop, responsive drawer on mobile, URL deep linking |
| **Client State Management** | Riverpod (`StateNotifierProvider`) | **Zustand** | Minimalist, unopinionated stores (`useAuthStore`, `useTaskStore`, `useHabitStore`, `useFocusStore`) |
| **Server State & Caching** | Riverpod + Dio in-memory list | **TanStack Query (React Query v5)** | Automatic background refetching, cache invalidation, optimistic UI updates |
| **HTTP Communication** | Dio with interceptors | **Axios** | JWT bearer token interceptor, centralized error handling, offline queue interception |
| **Data Visualizations** | FL Chart | **Recharts** | Responsive SVG charts (AreaChart for velocity, BarChart for categories, RadialBar for completion) |
| **Calendar & Time Blocking** | Table Calendar | **FullCalendar / Custom Big Calendar** | Week, Day, Month, Agenda views with drag-and-drop rescheduling and time block conflict warnings |
| **Icons** | Material Icons | **Lucide React** | Ultra-crisp vector icons for all features |
| **Notifications** | Flutter Local Notifications | **Browser Notifications API + Service Worker** | In-app toast alerts + native desktop/mobile browser push notifications with permission handling |
| **Local Persistence** | SharedPreferences | **localStorage + IndexedDB** | Instant offline reads/writes, cached user session, and persistent offline sync queue |
| **Offline & PWA** | Android Manifest / APK | **Vite PWA (`vite-plugin-pwa`)** | `manifest.json`, Service Worker caching offline shell and assets, installable on mobile & desktop |

---

## 3. New Backend Requirements (Friend Growth & Growth Couple)

To support the two new modules requested in the master prompt, we will expand the FastAPI backend with:

### Module 1: Friend Growth (`backend/app/models/friendship.py`, `schemas/friendship.py`, `services/friend_service.py`, `endpoints/friends.py`)
1. **User Discovery & Friend Requests**: Search users by email or username; send, accept, reject, or block friend requests.
2. **Shared Challenges**: Create group challenges (e.g. *"30-Day Cybersecurity & LeetCode Sprint"*).
3. **Accountability & Progress**: Track individual vs. group targets; share milestones.
4. **Encouragement Messages & Activity Feed**: Send cheer-ups; view friends' public achievements with strict privacy controls.
5. **Focus-Together Sessions**: Synchronized Pomodoro sessions with friends.

### Module 2: Growth Couple (`backend/app/models/couple.py`, `schemas/couple.py`, `services/couple_service.py`, `endpoints/couple.py`)
1. **Secure Partner Pairing**: One-to-one pairing via unique invitation code with accept/reject/unpair controls.
2. **Shared Goals & Habits**: Synchronized goals with dual progress tracking (Partner A % + Partner B % = Combined %).
3. **Shared Couple Calendar**: Coordinated calendar for joint study sessions, workouts, and check-ins.
4. **Daily Check-Ins & Weekly Growth Reviews**: Partner mood, gratitude, and weekly progress reflection.
5. **AI Growth Suggestions**: AI coach recommendations tailored specifically for joint couple aspirations.

### Strict Privacy & Authorization Rules
- Private personal tasks, notes, and individual calendar entries remain **strictly private** by default.
- Zero data leakage: database query filters strictly enforce friendship/couple authorization on every query.

---

## 4. Proposed Web Architecture & Project Structure

```
planner/
│
├── frontend/                          # NEW: React Web Application
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── icon-192.png
│   │   ├── icon-512.png
│   │   └── manifest.webmanifest      # PWA Manifest
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/                # Button, Card, Badge, Modal, Input, EmptyState
│   │   │   └── layout/                # Sidebar, Navbar, MobileNav, AppLayout, RightPanel
│   │   ├── features/
│   │   │   ├── auth/                  # Login, Register, Profile
│   │   │   ├── dashboard/             # Stats row, Productivity score, Today schedule
│   │   │   ├── tasks/                 # Task list, Create modal, Subtasks, Filters
│   │   │   ├── calendar/              # FullCalendar / Time blocking, Conflict banner
│   │   │   ├── ai-planner/            # NL quick add, Daily schedule, Weekly plan, Chat
│   │   │   ├── habits/                # Habit checklist, Streak counters, Best streak
│   │   │   ├── focus/                 # Pomodoro timer, Mode switch, Linked task
│   │   │   ├── kanban/                # To Do, In Progress, Completed drag & drop
│   │   │   ├── eisenhower/            # 4-quadrant triage matrix
│   │   │   ├── goals/                 # Long-term goals, Milestone tracker
│   │   │   ├── friend-growth/         # NEW: Friend requests, Challenges, Group accountability
│   │   │   ├── growth-couple/         # NEW: Partner pairing, Shared habits, Joint goals
│   │   │   ├── analytics/             # Recharts velocity charts, Category bars, Peak hours
│   │   │   └── settings/              # Theme switch, Notifications, Account
│   │   ├── hooks/                     # useAuth, useTasks, useNotifications, useOfflineSync
│   │   ├── services/                  # Axios API clients
│   │   ├── store/                     # Zustand stores (auth, task, habit, focus, theme)
│   │   ├── types/                     # TypeScript types mirroring Pydantic models
│   │   ├── utils/                     # Date formatters, priority helpers
│   │   ├── routes/                    # React Router configuration
│   │   ├── App.tsx                    # Root App component
│   │   ├── main.tsx                   # Entry point
│   │   └── index.css                  # Tailwind directives & CSS variables
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── backend/                           # PRESERVED & EXPANDED: FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/          # Existing endpoints + friends.py + couple.py
│   │   ├── models/                    # Existing models + friendship.py + couple.py
│   │   ├── schemas/                   # Existing schemas + friendship.py + couple.py
│   │   ├── services/                  # Existing services + friend_service.py + couple_service.py
│   │   ├── ai/                        # Existing AI schedulers, agents, anti-boredom
│   │   ├── core/                      # Security, JWT, Middleware, Config
│   │   └── tests/                     # 29 existing tests + new friend/couple tests
│   └── requirements.txt
│
├── lib/                               # PRESERVED: Original Flutter files (untouched)
├── PROJECT_PROGRESS.md
├── README.md
└── DEPLOYMENT.md
```

---

## 5. Phase-by-Phase Migration Checklist

### Phase 1: Existing Project Inspection & Architecture (COMPLETED)
- [x] Inspect existing Flutter codebase (`lib/`) and identify all 32 components and features.
- [x] Inspect existing FastAPI backend (`backend/app/`) and verify all 29 tests pass.
- [x] Map Flutter technologies to web equivalents (React, Vite, TypeScript, Tailwind, Zustand, Recharts).
- [x] Architect new social features: **Friend Growth** and **Growth Couple**.
- [x] Document the complete conversion plan in `CONVERSION_PLAN.md`.

### Phase 2: Website Foundation (NEXT)
- [ ] Initialize `frontend` directory using React + TypeScript + Vite.
- [ ] Configure Tailwind CSS with PlanWise Violet theme and dark mode.
- [ ] Install and configure Lucide React, Zustand, TanStack Query, and React Router DOM.
- [ ] Build desktop sidebar navigation, mobile navigation drawer, and top header with connection status.
- [ ] Implement responsive dashboard screen with live stats, greeting, and quick actions.

### Phase 3: Backend Extensions & Authentication
- [ ] Expand FastAPI backend with `Friendship` and `Couple` models, schemas, and endpoints.
- [ ] Add Firebase Web Auth compatibility layer.
- [ ] Connect React `useAuthStore` to backend `/api/v1/auth` endpoints.
- [ ] Test login, registration, and token persistence in browser `localStorage`.

### Phase 4: Core Productivity Features (Web)
- [ ] Migrate Tasks view (CRUD, subtasks, checklists, priorities, category filter chips).
- [ ] Migrate Calendar view with time-blocking grid, agenda view, and conflict detection banner.
- [ ] Migrate Habits tracker with interactive streak count checkmarks.
- [ ] Migrate Pomodoro Focus timer with circular SVG countdown and linked task logging.
- [ ] Migrate Kanban board (To Do, In Progress, Completed).
- [ ] Migrate Eisenhower 4-quadrant matrix.
- [ ] Migrate Goals and Milestones with auto-calculating progress bars.

### Phase 5: AI Web Features
- [ ] Migrate Natural Language Quick-Add bar with instant task parsing preview.
- [ ] Implement interactive AI Daily Scheduler with energy curve timeline and break slots.
- [ ] Implement Weekly Workload Balancer with 8-hour cap warnings.
- [ ] Implement AI Assistant Chat with quick prompt pills (*"Plan my day"*, *"What tasks are overdue?"*).
- [ ] Implement AI Goal Breakdown and Personal Productivity Coach insights.

### Phase 6: Social Growth Features (NEW)
- [ ] Build **Friend Growth** page: user search, send/accept requests, friends list, shared challenges, encouragement messages, and activity feed.
- [ ] Build **Growth Couple** page: partner invite code generator, pairing confirmation, shared habits, joint goals, couple check-ins, and AI couple growth advice.
- [ ] Verify strict privacy controls (private tasks remain invisible to friends/partners).

### Phase 7: Analytics & PWA Offline
- [ ] Build Analytics Dashboard using Recharts (velocity trends, category bars, focus minutes).
- [ ] Configure Vite PWA plugin with `manifest.webmanifest` and Service Worker.
- [ ] Implement offline task viewing and persistent sync queue in browser storage.
- [ ] Verify Last-Write-Wins (LWW) conflict resolution between web client and backend.

### Phase 8: Testing, Polish & Deployment Documentation
- [ ] Run backend pytest suite (verify existing 29 tests + new friend/couple tests).
- [ ] Verify full responsive UI on desktop, tablet, and mobile viewport sizes.
- [ ] Create `DEPLOYMENT.md` with Vercel (frontend), Render (backend), and Firebase setup guides.
- [ ] Update `README.md` and `PROJECT_PROGRESS.md`.

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/dashboard/presentation/screens/dashboard_screen.dart';
import '../features/tasks/presentation/screens/tasks_screen.dart';
import '../features/calendar/presentation/screens/calendar_screen.dart';
import '../features/ai_planner/presentation/screens/ai_planner_screen.dart';
import '../features/habits/presentation/screens/habits_screen.dart';
import '../features/focus/presentation/screens/focus_screen.dart';
import '../features/goals/presentation/screens/goals_screen.dart';
import '../features/analytics/presentation/screens/analytics_screen.dart';
import '../features/settings/presentation/screens/settings_screen.dart';
import '../shared/widgets/bottom_nav_shell.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>();

final appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/',
  routes: [
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) {
        return BottomNavShell(navigationShell: navigationShell);
      },
      branches: [
        // Branch 1: Dashboard
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/',
              builder: (context, state) => DashboardScreen(
                onNavigateToTasks: () => context.go('/tasks'),
                onNavigateToCalendar: () => context.go('/calendar'),
                onNavigateToAiPlanner: () => context.go('/ai-planner'),
                onNavigateToHabits: () => context.push('/habits'),
                onNavigateToFocus: () => context.push('/focus'),
              ),
            ),
          ],
        ),
        // Branch 2: Tasks
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/tasks',
              builder: (context, state) => const TasksScreen(),
            ),
          ],
        ),
        // Branch 3: Calendar
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/calendar',
              builder: (context, state) => const CalendarScreen(),
            ),
          ],
        ),
        // Branch 4: AI Planner
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/ai-planner',
              builder: (context, state) => const AiPlannerScreen(),
            ),
          ],
        ),
        // Branch 5: Settings / More
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/more',
              builder: (context, state) => const SettingsScreen(),
            ),
          ],
        ),
      ],
    ),
    // Sub-routes pushed on top of the root navigator
    GoRoute(
      path: '/habits',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const HabitsScreen(),
    ),
    GoRoute(
      path: '/focus',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const FocusScreen(),
    ),
    GoRoute(
      path: '/goals',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const GoalsScreen(),
    ),
    GoRoute(
      path: '/analytics',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const AnalyticsScreen(),
    ),
    GoRoute(
      path: '/settings',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);

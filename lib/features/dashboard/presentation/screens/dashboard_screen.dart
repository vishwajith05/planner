import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../shared/models/priority.dart';
import '../widgets/productivity_score_card.dart';
import '../widgets/quick_actions_card.dart';
import '../widgets/stats_overview_row.dart';
import '../widgets/today_tasks_preview.dart';

class DashboardScreen extends StatelessWidget {
  final VoidCallback? onNavigateToTasks;
  final VoidCallback? onNavigateToCalendar;
  final VoidCallback? onNavigateToAiPlanner;
  final VoidCallback? onNavigateToHabits;
  final VoidCallback? onNavigateToFocus;

  const DashboardScreen({
    Key? key,
    this.onNavigateToTasks,
    this.onNavigateToCalendar,
    this.onNavigateToAiPlanner,
    this.onNavigateToHabits,
    this.onNavigateToFocus,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final sampleTasks = [
      const DashboardTaskItem(
        id: '1',
        title: 'Review Cybersecurity Network Security Architecture',
        time: '09:00 AM - 10:30 AM',
        category: 'Cybersecurity',
        priority: TaskPriority.urgent,
        isCompleted: true,
      ),
      const DashboardTaskItem(
        id: '2',
        title: 'Implement FastAPI Deterministic Scheduler Engine',
        time: '11:00 AM - 12:30 PM',
        category: 'Programming',
        priority: TaskPriority.high,
        isCompleted: false,
      ),
      const DashboardTaskItem(
        id: '3',
        title: 'Deep Work: Flutter State Management & Clean Architecture',
        time: '02:00 PM - 03:30 PM',
        category: 'Education',
        priority: TaskPriority.medium,
        isCompleted: false,
      ),
      const DashboardTaskItem(
        id: '4',
        title: 'Evening Physical Conditioning & Hydration',
        time: '06:00 PM - 06:45 PM',
        category: 'Health',
        priority: TaskPriority.low,
        isCompleted: false,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.bolt, color: AppColors.primary, size: 20),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'PlanWise AI',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Plan Smarter. Achieve More.',
                  style: TextStyle(fontSize: 11, color: AppColors.lightTextSecondary),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Quick search activated')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.notifications_none_outlined),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Notifications view')),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.delayed(const Duration(milliseconds: 600));
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // User Greeting Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Good day, Architect',
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Here is your intelligent daily productivity briefing.',
                        style: TextStyle(color: AppColors.lightTextSecondary, fontSize: 13),
                      ),
                    ],
                  ),
                  CircleAvatar(
                    backgroundColor: AppColors.primary.withOpacity(0.15),
                    radius: 20,
                    child: const Icon(Icons.person, color: AppColors.primary),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Productivity Index & AI Recommendation
              const ProductivityScoreCard(),
              const SizedBox(height: 14),

              // Stats Row (Done, Pending, Focus, Habits)
              const StatsOverviewRow(),
              const SizedBox(height: 20),

              // Quick Actions
              QuickActionsCard(
                onQuickAdd: onNavigateToTasks,
                onAiPlan: onNavigateToAiPlanner,
                onStartFocus: onNavigateToFocus,
                onHabits: onNavigateToHabits,
              ),
              const SizedBox(height: 22),

              // Today's Scheduled Tasks
              TodayTasksPreview(
                tasks: sampleTasks,
                onViewAll: onNavigateToTasks,
                onToggleTask: (id, completed) {
                  // Task toggle
                },
              ),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }
}

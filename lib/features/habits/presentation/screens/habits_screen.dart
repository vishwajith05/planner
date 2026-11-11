import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';

class HabitItem {
  final String id;
  final String title;
  final String description;
  final String category;
  final int streak;
  bool isCompletedToday;

  HabitItem({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.streak,
    this.isCompletedToday = false,
  });
}

class HabitsScreen extends StatefulWidget {
  const HabitsScreen({Key? key}) : super(key: key);

  @override
  State<HabitsScreen> createState() => _HabitsScreenState();
}

class _HabitsScreenState extends State<HabitsScreen> {
  final List<HabitItem> _habits = [
    HabitItem(
      id: 'h1',
      title: 'Daily LeetCode Problem',
      description: 'Solve 1 algorithmic or data structures problem',
      category: 'Programming',
      streak: 14,
      isCompletedToday: true,
    ),
    HabitItem(
      id: 'h2',
      title: 'Cybersecurity Whitepaper Reading',
      description: 'Read 20 minutes of latest threat intelligence',
      category: 'Cybersecurity',
      streak: 8,
      isCompletedToday: true,
    ),
    HabitItem(
      id: 'h3',
      title: 'Morning Hydration & Stretching',
      description: 'Drink 500ml water and complete 10 mins mobility',
      category: 'Health',
      streak: 21,
      isCompletedToday: true,
    ),
    HabitItem(
      id: 'h4',
      title: 'Deep Focus Sprint (No Phone)',
      description: 'At least one 50-minute uninterrupted deep work block',
      category: 'Personal',
      streak: 5,
      isCompletedToday: false,
    ),
  ];

  void _addNewHabitDialog() {
    final titleCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create New Habit'),
        content: TextField(
          controller: titleCtrl,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Habit Title',
            hintText: 'e.g. Read 15 pages of system design book',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (titleCtrl.text.trim().isNotEmpty) {
                setState(() {
                  _habits.add(
                    HabitItem(
                      id: 'h-${DateTime.now().millisecondsSinceEpoch}',
                      title: titleCtrl.text.trim(),
                      description: 'Daily consistency target',
                      category: 'Personal',
                      streak: 0,
                      isCompletedToday: false,
                    ),
                  );
                });
                Navigator.pop(ctx);
              }
            },
            child: const Text('Create Habit'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final completedCount = _habits.where((h) => h.isCompletedToday).length;
    final totalCount = _habits.length;
    final completionPct = totalCount > 0 ? (completedCount / totalCount * 100).round() : 0;
    final maxStreak = _habits.map((h) => h.streak).fold(0, (max, v) => v > max ? v : max);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Habits & Streaks'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Habit Progress Stats Banner
          AppCard(
            color: Theme.of(context).brightness == Brightness.dark
                ? AppColors.darkSurfaceVariant.withOpacity(0.5)
                : AppColors.statusWarning.withOpacity(0.08),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _StatColumn(label: 'Done Today', value: '$completedCount / $totalCount'),
                Container(width: 1, height: 36, color: AppColors.lightBorder),
                _StatColumn(label: 'Rate', value: '$completionPct%'),
                Container(width: 1, height: 36, color: AppColors.lightBorder),
                _StatColumn(label: 'Max Streak', value: '🔥 $maxStreak d'),
              ],
            ),
          ),
          const SizedBox(height: 18),

          const Text(
            'Today\'s Active Habits',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),

          ..._habits.map((habit) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 10.0),
              child: AppCard(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                child: Row(
                  children: [
                    InkWell(
                      onTap: () {
                        setState(() {
                          habit.isCompletedToday = !habit.isCompletedToday;
                        });
                      },
                      borderRadius: BorderRadius.circular(20),
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: habit.isCompletedToday
                              ? AppColors.statusSuccess
                              : Colors.transparent,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: habit.isCompletedToday
                                ? AppColors.statusSuccess
                                : AppColors.lightBorder,
                            width: 2,
                          ),
                        ),
                        child: Icon(
                          Icons.check,
                          size: 18,
                          color: habit.isCompletedToday ? Colors.white : Colors.transparent,
                        ),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            habit.title,
                            style: TextStyle(
                              fontSize: 14.5,
                              fontWeight: FontWeight.w600,
                              decoration: habit.isCompletedToday ? TextDecoration.lineThrough : null,
                              color: habit.isCompletedToday ? AppColors.lightTextSecondary : null,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            habit.description,
                            style: const TextStyle(fontSize: 12, color: AppColors.lightTextSecondary),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.statusWarning.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppColors.statusWarning.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.local_fire_department, size: 14, color: AppColors.statusWarning),
                          const SizedBox(width: 2),
                          Text(
                            '${habit.streak}',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: AppColors.statusWarning,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('New Habit'),
        onPressed: _addNewHabitDialog,
      ),
    );
  }
}

class _StatColumn extends StatelessWidget {
  final String label;
  final String value;

  const _StatColumn({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.lightTextSecondary)),
      ],
    );
  }
}

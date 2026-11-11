import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';

class MilestoneItem {
  final String id;
  final String title;
  bool isCompleted;

  MilestoneItem({required this.id, required this.title, this.isCompleted = false});
}

class GoalItem {
  final String id;
  final String title;
  final String description;
  final String category;
  final List<MilestoneItem> milestones;

  GoalItem({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.milestones,
  });

  double get progressPercentage {
    if (milestones.isEmpty) return 0.0;
    final done = milestones.where((m) => m.isCompleted).length;
    return (done / milestones.length) * 100.0;
  }
}

class GoalsScreen extends StatefulWidget {
  const GoalsScreen({Key? key}) : super(key: key);

  @override
  State<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  final List<GoalItem> _goals = [
    GoalItem(
      id: 'g1',
      title: 'Become a Cybersecurity Specialist',
      description: 'Master network protocols, penetration testing, and security compliance',
      category: 'Cybersecurity',
      milestones: [
        MilestoneItem(id: 'm1', title: 'Learn networking fundamentals & TCP/IP', isCompleted: true),
        MilestoneItem(id: 'm2', title: 'Linux administration and shell scripting', isCompleted: true),
        MilestoneItem(id: 'm3', title: 'CompTIA Security+ or CEH certification', isCompleted: false),
        MilestoneItem(id: 'm4', title: 'Build security labs & publish writeups', isCompleted: false),
      ],
    ),
    GoalItem(
      id: 'g2',
      title: 'Full-Stack Flutter & AI Systems Mastery',
      description: 'Ship production-grade AI-powered applications',
      category: 'Programming',
      milestones: [
        MilestoneItem(id: 'm5', title: 'Advanced Riverpod & GoRouter architecture', isCompleted: true),
        MilestoneItem(id: 'm6', title: 'Deterministic scheduling algorithm design', isCompleted: true),
        MilestoneItem(id: 'm7', title: 'Deploy FastAPI backend with multi-provider AI', isCompleted: true),
      ],
    ),
  ];

  void _addGoalDialog() {
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create Long-Term Goal'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleCtrl,
              autofocus: true,
              decoration: const InputDecoration(labelText: 'Goal Title *', hintText: 'e.g. Master Machine Learning'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: descCtrl,
              decoration: const InputDecoration(labelText: 'Description', hintText: 'Target outcome and roadmap'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              if (titleCtrl.text.trim().isNotEmpty) {
                setState(() {
                  _goals.add(
                    GoalItem(
                      id: 'g-${DateTime.now().millisecondsSinceEpoch}',
                      title: titleCtrl.text.trim(),
                      description: descCtrl.text.trim(),
                      category: 'Personal',
                      milestones: [
                        MilestoneItem(id: 'm-new-1', title: 'Phase 1 Foundations', isCompleted: false),
                        MilestoneItem(id: 'm-new-2', title: 'Phase 2 Real Project', isCompleted: false),
                      ],
                    ),
                  );
                });
                Navigator.pop(ctx);
              }
            },
            child: const Text('Create Goal'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Goals & Milestones'),
      ),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _goals.length,
        separatorBuilder: (_, __) => const SizedBox(height: 14),
        itemBuilder: (context, index) {
          final goal = _goals[index];
          final progress = goal.progressPercentage;

          return AppCard(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        goal.category,
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary),
                      ),
                    ),
                    Text(
                      '${progress.round()}% Completed',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  goal.title,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                if (goal.description.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    goal.description,
                    style: const TextStyle(fontSize: 12, color: AppColors.lightTextSecondary),
                  ),
                ],
                const SizedBox(height: 10),

                // Linear Progress Indicator
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: progress / 100.0,
                    minHeight: 8,
                    backgroundColor: AppColors.lightBorder,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      progress >= 100.0 ? AppColors.statusSuccess : AppColors.primary,
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // Milestones list
                const Text('Milestones', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                ...goal.milestones.map((milestone) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2.0),
                    child: Row(
                      children: [
                        Checkbox(
                          value: milestone.isCompleted,
                          activeColor: AppColors.statusSuccess,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          onChanged: (val) {
                            setState(() {
                              milestone.isCompleted = val ?? false;
                            });
                          },
                        ),
                        Expanded(
                          child: Text(
                            milestone.title,
                            style: TextStyle(
                              fontSize: 13,
                              decoration: milestone.isCompleted ? TextDecoration.lineThrough : null,
                              color: milestone.isCompleted ? AppColors.lightTextSecondary : null,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.flag_outlined),
        label: const Text('New Goal'),
        onPressed: _addGoalDialog,
      ),
    );
  }
}

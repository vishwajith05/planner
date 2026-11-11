import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/priority_badge.dart';
import '../../../../shared/models/priority.dart';

class KanbanTask {
  final String id;
  final String title;
  final String category;
  final TaskPriority priority;
  String status; // 'todo', 'in_progress', 'completed'

  KanbanTask({
    required this.id,
    required this.title,
    required this.category,
    required this.priority,
    required this.status,
  });
}

class KanbanScreen extends StatefulWidget {
  const KanbanScreen({Key? key}) : super(key: key);

  @override
  State<KanbanScreen> createState() => _KanbanScreenState();
}

class _KanbanScreenState extends State<KanbanScreen> {
  final List<KanbanTask> _tasks = [
    KanbanTask(
      id: 'k1',
      title: 'Review Cybersecurity Network Security Architecture',
      category: 'Cybersecurity',
      priority: TaskPriority.urgent,
      status: 'completed',
    ),
    KanbanTask(
      id: 'k2',
      title: 'Implement FastAPI Deterministic Scheduler Engine',
      category: 'Programming',
      priority: TaskPriority.high,
      status: 'in_progress',
    ),
    KanbanTask(
      id: 'k3',
      title: 'Deep Work: Flutter State Management & Clean Architecture',
      category: 'Education',
      priority: TaskPriority.medium,
      status: 'todo',
    ),
    KanbanTask(
      id: 'k4',
      title: 'Evening Physical Conditioning & Hydration',
      category: 'Health',
      priority: TaskPriority.low,
      status: 'todo',
    ),
  ];

  void _moveTask(KanbanTask task, String newStatus) {
    setState(() {
      task.status = newStatus;
    });
  }

  @override
  Widget build(BuildContext context) {
    final todoTasks = _tasks.where((t) => t.status == 'todo').toList();
    final inProgressTasks = _tasks.where((t) => t.status == 'in_progress').toList();
    final completedTasks = _tasks.where((t) => t.status == 'completed').toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Kanban Board'),
      ),
      body: PageView(
        children: [
          _buildColumn('To Do', todoTasks, AppColors.priorityMedium, 'todo'),
          _buildColumn('In Progress', inProgressTasks, AppColors.priorityHigh, 'in_progress'),
          _buildColumn('Completed', completedTasks, AppColors.statusSuccess, 'completed'),
        ],
      ),
    );
  }

  Widget _buildColumn(String title, List<KanbanTask> tasks, Color accentColor, String statusKey) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 10, height: 10, decoration: BoxDecoration(color: accentColor, shape: BoxShape.circle)),
              const SizedBox(width: 8),
              Text(
                '$title (${tasks.length})',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Expanded(
            child: tasks.isEmpty
                ? Center(
                    child: Text(
                      'No tasks in $title',
                      style: const TextStyle(color: AppColors.lightTextSecondary),
                    ),
                  )
                : ListView.separated(
                    itemCount: tasks.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 10),
                    itemBuilder: (context, index) {
                      final task = tasks[index];
                      return AppCard(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: AppColors.lightBorder.withOpacity(0.4),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(task.category, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500)),
                                ),
                                PriorityBadge(priority: task.priority),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              task.title,
                              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                            ),
                            const SizedBox(height: 10),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                if (statusKey != 'todo')
                                  TextButton(
                                    onPressed: () => _moveTask(task, statusKey == 'completed' ? 'in_progress' : 'todo'),
                                    child: const Text('← Move Back', style: TextStyle(fontSize: 12)),
                                  ),
                                if (statusKey != 'completed')
                                  ElevatedButton(
                                    onPressed: () => _moveTask(task, statusKey == 'todo' ? 'in_progress' : 'completed'),
                                    style: ElevatedButton.styleFrom(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      textStyle: const TextStyle(fontSize: 11),
                                    ),
                                    child: Text(statusKey == 'todo' ? 'Start →' : 'Done ✓'),
                                  ),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/priority_badge.dart';
import '../../../../shared/models/priority.dart';

class DashboardTaskItem {
  final String id;
  final String title;
  final String time;
  final String category;
  final TaskPriority priority;
  final bool isCompleted;

  const DashboardTaskItem({
    required this.id,
    required this.title,
    required this.time,
    required this.category,
    required this.priority,
    this.isCompleted = false,
  });
}

class TodayTasksPreview extends StatefulWidget {
  final List<DashboardTaskItem> tasks;
  final VoidCallback? onViewAll;
  final Function(String id, bool completed)? onToggleTask;

  const TodayTasksPreview({
    Key? key,
    required this.tasks,
    this.onViewAll,
    this.onToggleTask,
  }) : super(key: key);

  @override
  State<TodayTasksPreview> createState() => _TodayTasksPreviewState();
}

class _TodayTasksPreviewState extends State<TodayTasksPreview> {
  late Map<String, bool> completionMap;

  @override
  void initState() {
    super.initState();
    completionMap = {for (var t in widget.tasks) t.id: t.isCompleted};
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              "Today's Schedule",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: widget.onViewAll,
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 4),
        if (widget.tasks.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 24),
            child: Center(
              child: Text(
                'No tasks scheduled for today. Great job!',
                style: TextStyle(color: AppColors.lightTextSecondary),
              ),
            ),
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: widget.tasks.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final task = widget.tasks[index];
              final isDone = completionMap[task.id] ?? false;

              return AppCard(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                child: Row(
                  children: [
                    Checkbox(
                      value: isDone,
                      activeColor: AppColors.primary,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                      ),
                      onChanged: (val) {
                        setState(() {
                          completionMap[task.id] = val ?? false;
                        });
                        widget.onToggleTask?.call(task.id, val ?? false);
                      },
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            task.title,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              decoration: isDone ? TextDecoration.lineThrough : null,
                              color: isDone
                                  ? AppColors.lightTextSecondary
                                  : null,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Icon(Icons.access_time, size: 12, color: AppColors.lightTextSecondary),
                              const SizedBox(width: 4),
                              Text(
                                task.time,
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: AppColors.lightTextSecondary,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AppColors.lightBorder.withOpacity(0.4),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  task.category,
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    PriorityBadge(priority: task.priority),
                  ],
                ),
              );
            },
          ),
      ],
    );
  }
}

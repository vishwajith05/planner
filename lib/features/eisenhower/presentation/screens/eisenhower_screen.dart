import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';

class EisenhowerScreen extends StatelessWidget {
  const EisenhowerScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Eisenhower Priority Matrix'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            Expanded(
              child: Row(
                children: [
                  // Q1: Urgent & Important
                  Expanded(
                    child: _QuadrantCard(
                      title: 'Q1: DO FIRST',
                      subtitle: 'Urgent & Important',
                      accentColor: AppColors.priorityUrgent,
                      tasks: const [
                        'Review Network Security Architecture',
                        'Fix production critical vulnerability',
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  // Q2: Not Urgent & Important
                  Expanded(
                    child: _QuadrantCard(
                      title: 'Q2: SCHEDULE',
                      subtitle: 'Not Urgent & Important',
                      accentColor: AppColors.primary,
                      tasks: const [
                        'Deterministic Scheduler Engine',
                        'Flutter Clean Architecture Refactor',
                        'CompTIA Security+ Prep',
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: Row(
                children: [
                  // Q3: Urgent & Not Important
                  Expanded(
                    child: _QuadrantCard(
                      title: 'Q3: DELEGATE',
                      subtitle: 'Urgent & Not Important',
                      accentColor: AppColors.statusWarning,
                      tasks: const [
                        'Sort team meeting notes',
                        'Respond to vendor inquiry email',
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  // Q4: Not Urgent & Not Important
                  Expanded(
                    child: _QuadrantCard(
                      title: 'Q4: ELIMINATE',
                      subtitle: 'Not Urgent & Not Important',
                      accentColor: AppColors.lightTextSecondary,
                      tasks: const [
                        'Review obsolete documentation',
                        'Random social media feed browsing',
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _QuadrantCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final Color accentColor;
  final List<String> tasks;

  const _QuadrantCard({
    required this.title,
    required this.subtitle,
    required this.accentColor,
    required this.tasks,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 8, height: 8, decoration: BoxDecoration(color: accentColor, shape: BoxShape.circle)),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: accentColor),
                ),
              ),
            ],
          ),
          const SizedBox(height: 2),
          Text(subtitle, style: const TextStyle(fontSize: 11, color: AppColors.lightTextSecondary)),
          const Divider(height: 14),
          Expanded(
            child: ListView.separated(
              itemCount: tasks.length,
              separatorBuilder: (_, __) => const SizedBox(height: 6),
              itemBuilder: (context, index) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                    Expanded(
                      child: Text(
                        tasks[index],
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

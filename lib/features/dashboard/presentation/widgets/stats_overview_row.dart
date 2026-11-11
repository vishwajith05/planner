import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';

class StatsOverviewRow extends StatelessWidget {
  final int completedTasks;
  final int pendingTasks;
  final int focusMinutes;
  final int activeHabits;

  const StatsOverviewRow({
    Key? key,
    this.completedTasks = 5,
    this.pendingTasks = 3,
    this.focusMinutes = 75,
    this.activeHabits = 4,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            label: 'Done',
            value: '$completedTasks',
            icon: Icons.check_circle_outline,
            iconColor: AppColors.statusSuccess,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            label: 'Pending',
            value: '$pendingTasks',
            icon: Icons.pending_actions_outlined,
            iconColor: AppColors.priorityHigh,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            label: 'Focus',
            value: '${focusMinutes}m',
            icon: Icons.timer_outlined,
            iconColor: AppColors.primary,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            label: 'Habits',
            value: '$activeHabits/5',
            icon: Icons.local_fire_department,
            iconColor: AppColors.statusWarning,
          ),
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color iconColor;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: iconColor),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: AppColors.lightTextSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

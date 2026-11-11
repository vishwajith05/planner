import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';

class QuickActionsCard extends StatelessWidget {
  final VoidCallback? onQuickAdd;
  final VoidCallback? onAiPlan;
  final VoidCallback? onStartFocus;
  final VoidCallback? onHabits;

  const QuickActionsCard({
    Key? key,
    this.onQuickAdd,
    this.onAiPlan,
    this.onStartFocus,
    this.onHabits,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Actions',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 10),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _ActionButton(
              icon: Icons.add_task,
              label: 'Add Task',
              color: AppColors.primary,
              onTap: onQuickAdd,
            ),
            _ActionButton(
              icon: Icons.psychology,
              label: 'AI Plan Day',
              color: AppColors.accent,
              onTap: onAiPlan,
            ),
            _ActionButton(
              icon: Icons.play_arrow_rounded,
              label: 'Start Focus',
              color: AppColors.priorityHigh,
              onTap: onStartFocus,
            ),
            _ActionButton(
              icon: Icons.track_changes,
              label: 'Check Habit',
              color: AppColors.statusSuccess,
              onTap: onHabits,
            ),
          ],
        ),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback? onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 80,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 6),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

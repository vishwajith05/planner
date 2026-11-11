import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/empty_state.dart';

class AiPlannerScreen extends StatelessWidget {
  const AiPlannerScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Daily & Weekly Planner'),
      ),
      body: EmptyStateWidget(
        icon: Icons.psychology_outlined,
        title: 'Intelligent AI Scheduling Engine',
        message: 'Deterministic scheduler with energy-level pacing, anti-boredom switching, and conflict resolution.',
        actionLabel: 'Generate Schedule',
        onAction: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('AI Scheduling Engine connected to backend')),
          );
        },
      ),
    );
  }
}

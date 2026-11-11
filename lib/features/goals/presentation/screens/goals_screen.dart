import 'package:flutter/material.dart';
import '../../../../core/widgets/empty_state.dart';

class GoalsScreen extends StatelessWidget {
  const GoalsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Goals & Milestones'),
      ),
      body: const EmptyStateWidget(
        icon: Icons.flag_outlined,
        title: 'Long-Term Goal Hierarchy',
        message: 'Goal breakdown, milestone progression, and AI-suggested learning roadmap in Phase 4.',
      ),
    );
  }
}

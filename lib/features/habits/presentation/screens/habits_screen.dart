import 'package:flutter/material.dart';
import '../../../../core/widgets/empty_state.dart';

class HabitsScreen extends StatelessWidget {
  const HabitsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Habits & Streaks'),
      ),
      body: const EmptyStateWidget(
        icon: Icons.local_fire_department_outlined,
        title: 'Habit Consistency Engine',
        message: 'Daily and weekly habits, streak tracking, and completion percentage visualizer in Phase 4.',
      ),
    );
  }
}

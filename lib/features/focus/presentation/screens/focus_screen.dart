import 'package:flutter/material.dart';
import '../../../../core/widgets/empty_state.dart';

class FocusScreen extends StatelessWidget {
  const FocusScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Focus & Pomodoro Timer'),
      ),
      body: const EmptyStateWidget(
        icon: Icons.timer_outlined,
        title: 'Deep Focus & Pomodoro Engine',
        message: 'Customizable 25/5/15 minute intervals with task linkage and background persistence.',
      ),
    );
  }
}

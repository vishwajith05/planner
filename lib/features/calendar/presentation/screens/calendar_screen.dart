import 'package:flutter/material.dart';
import '../../../../core/widgets/empty_state.dart';

class CalendarScreen extends StatelessWidget {
  const CalendarScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Calendar & Time Blocking'),
      ),
      body: const EmptyStateWidget(
        icon: Icons.calendar_month_rounded,
        title: 'Interactive Time Blocking',
        message: 'Day, Week, Month and Agenda views with conflict detection scheduled for Phase 3.',
      ),
    );
  }
}

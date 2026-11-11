import 'package:flutter/material.dart';
import '../../../../core/widgets/empty_state.dart';

class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Productivity Analytics'),
      ),
      body: const EmptyStateWidget(
        icon: Icons.insights_outlined,
        title: 'Real-Time Productivity Intelligence',
        message: 'Completion trends, category breakdown, focus analytics, and peak energy detection in Phase 5.',
      ),
    );
  }
}

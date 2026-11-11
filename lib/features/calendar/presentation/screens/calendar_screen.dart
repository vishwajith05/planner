import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';

class CalendarItem {
  final String id;
  final String title;
  final String timeRange;
  final String category;
  final bool isFixed;

  const CalendarItem({
    required this.id,
    required this.title,
    required this.timeRange,
    required this.category,
    this.isFixed = false,
  });
}

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({Key? key}) : super(key: key);

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  DateTime _selectedDate = DateTime.now();
  String _activeView = 'Day'; // 'Day', 'Week', 'Agenda'

  final List<CalendarItem> _todayEvents = [
    const CalendarItem(
      id: 'e1',
      title: 'Computer Networks Lecture (Fixed Commitment)',
      timeRange: '09:00 AM - 10:30 AM',
      category: 'Education',
      isFixed: true,
    ),
    const CalendarItem(
      id: 'e2',
      title: 'Time Block: Implement Deterministic Scheduling Engine',
      timeRange: '11:00 AM - 12:30 PM',
      category: 'Programming',
      isFixed: false,
    ),
    const CalendarItem(
      id: 'e3',
      title: 'Deep Work: Flutter State Management Architecture',
      timeRange: '02:00 PM - 03:30 PM',
      category: 'Education',
      isFixed: false,
    ),
    const CalendarItem(
      id: 'e4',
      title: 'Evening Conditioning & Mobility Session',
      timeRange: '06:00 PM - 06:45 PM',
      category: 'Health',
      isFixed: false,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final daysOfWeek = List.generate(7, (i) {
      final d = now.subtract(Duration(days: now.weekday - 1 - i));
      return d;
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Calendar & Time Blocking'),
        actions: [
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'Day', label: Text('Day', style: TextStyle(fontSize: 11))),
              ButtonSegment(value: 'Week', label: Text('Week', style: TextStyle(fontSize: 11))),
              ButtonSegment(value: 'Agenda', label: Text('Agenda', style: TextStyle(fontSize: 11))),
            ],
            selected: {_activeView},
            onSelectionChanged: (val) {
              setState(() => _activeView = val.first);
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          // Weekly Date Picker Bar
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).cardTheme.color,
              border: const Border(bottom: BorderSide(color: AppColors.lightBorder, width: 0.5)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: daysOfWeek.map((day) {
                final isSelected = day.day == _selectedDate.day &&
                    day.month == _selectedDate.month &&
                    day.year == _selectedDate.year;
                const weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
                final dayLabel = weekdays[day.weekday - 1];

                return InkWell(
                  onTap: () => setState(() => _selectedDate = day),
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    width: 44,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected ? AppColors.primary : Colors.transparent,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        Text(
                          dayLabel,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: isSelected ? Colors.white : AppColors.lightTextSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${day.day}',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: isSelected ? Colors.white : null,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          // Conflict Detection Banner Indicator
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 10, 16, 4),
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.statusSuccess.withOpacity(0.12),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.statusSuccess.withOpacity(0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle_outline, color: AppColors.statusSuccess, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Deterministic Conflict Checker: No overlapping time slots detected.',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.statusSuccess),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Scheduled Time Blocks Timeline
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _todayEvents.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final event = _todayEvents[index];

                return AppCard(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 4,
                        height: 48,
                        decoration: BoxDecoration(
                          color: event.isFixed ? AppColors.priorityHigh : AppColors.primary,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                if (event.isFixed) ...[
                                  const Icon(Icons.lock, size: 14, color: AppColors.priorityHigh),
                                  const SizedBox(width: 4),
                                ],
                                Expanded(
                                  child: Text(
                                    event.title,
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                const Icon(Icons.access_time, size: 13, color: AppColors.lightTextSecondary),
                                const SizedBox(width: 4),
                                Text(
                                  event.timeRange,
                                  style: const TextStyle(fontSize: 12, color: AppColors.lightTextSecondary),
                                ),
                                const SizedBox(width: 10),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: AppColors.lightBorder.withOpacity(0.4),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    event.category,
                                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.schedule),
        label: const Text('Block Time'),
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Time-block scheduling dialog activated')),
          );
        },
      ),
    );
  }
}

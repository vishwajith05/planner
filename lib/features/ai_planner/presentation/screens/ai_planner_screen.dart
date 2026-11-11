import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/priority_badge.dart';

class AiPlannerScreen extends StatefulWidget {
  const AiPlannerScreen({Key? key}) : super(key: key);

  @override
  State<AiPlannerScreen> createState() => _AiPlannerScreenState();
}

class _AiPlannerScreenState extends State<AiPlannerScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _promptController = TextEditingController();
  final TextEditingController _chatController = TextEditingController();

  final List<Map<String, String>> _chatMessages = [
    {
      'sender': 'assistant',
      'text':
          'Hello! I am PlanWise AI. Ask me to "Plan my day", audit overdue tasks, or break down any complex goal into milestones.',
    }
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _promptController.dispose();
    _chatController.dispose();
    super.dispose();
  }

  void _sendChatMessage(String text) {
    if (text.trim().isEmpty) return;
    setState(() {
      _chatMessages.add({'sender': 'user', 'text': text});
      _chatController.clear();
    });

    // Simulated local reactive response based on real agent capabilities
    Future.delayed(const Duration(milliseconds: 600), () {
      final low = text.toLowerCase();
      String reply;
      if (low.contains('plan my day') || low.contains('schedule')) {
        reply =
            '📅 I have compiled an optimal 5-task schedule for today (4.5 hrs total) with 10-min rest buffers between intense blocks. High priority items are aligned with your 10 AM peak window.';
      } else if (low.contains('overdue')) {
        reply =
            '🔍 Audited your tasks: 1 item is past due ("Security Architecture Review"). Would you like me to move it to tomorrow at 2 PM?';
      } else if (low.contains('goal')) {
        reply =
            '🎯 Breaking down your goal into 4 structured milestones: 1) Fundamentals (14 days), 2) Hands-on labs (21 days), 3) Capstone project (14 days), 4) Final assessment.';
      } else {
        reply =
            'I can help you organize tasks, optimize your daily energy rhythm, and monitor streaks. Try asking "Plan my day"!';
      }
      setState(() {
        _chatMessages.add({'sender': 'assistant', 'text': reply});
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Productivity Engine'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.primaryViolet,
          labelColor: AppColors.primaryViolet,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(icon: Icon(Icons.calendar_today_outlined), text: 'Daily Plan'),
            Tab(icon: Icon(Icons.view_week_outlined), text: 'Weekly'),
            Tab(icon: Icon(Icons.chat_bubble_outline), text: 'AI Assistant'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildDailyPlannerTab(),
          _buildWeeklyPlannerTab(),
          _buildAssistantChatTab(),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 1: Daily Schedule Generator & Timeline
  // ---------------------------------------------------------------------------
  Widget _buildDailyPlannerTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Natural Language Task Interpreter Bar
          AppCard(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                const Icon(Icons.auto_awesome, color: AppColors.primaryViolet),
                const SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: _promptController,
                    decoration: const InputDecoration(
                      hintText: 'e.g. Study Python tomorrow at 6 AM for 1 hour',
                      border: InputBorder.none,
                      isDense: true,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send_rounded, color: AppColors.primaryViolet),
                  onPressed: () {
                    final prompt = _promptController.text;
                    if (prompt.isNotEmpty) {
                      _promptController.clear();
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('AI parsed task: "$prompt"')),
                      );
                    }
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Workload Banner
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.primaryViolet.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.primaryViolet.withOpacity(0.3)),
            ),
            child: Row(
              children: const [
                Icon(Icons.bolt, color: AppColors.primaryViolet),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Energy-Aware Scheduling: Slots aligned with your cognitive peak (10 AM - 12 PM).',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Action Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Today's AI Schedule",
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              AppButton(
                label: 'Regenerate',
                icon: Icons.refresh,
                type: AppButtonType.secondary,
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Recalculating deterministic energy schedule...')),
                  );
                },
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Timeline Slots
          _buildScheduleSlot(
            time: '08:30 - 09:15 AM',
            title: 'Algorithm Problem Solving',
            category: 'Programming',
            priority: 'high',
            energy: 'High (Peak)',
          ),
          _buildScheduleSlot(
            time: '09:30 - 11:00 AM',
            title: 'Build Secure API Endpoints',
            category: 'Cybersecurity',
            priority: 'urgent',
            energy: 'Peak Energy',
          ),
          _buildBreakSlot(time: '11:00 - 11:15 AM', title: '15-min Rest & Hydration Break'),
          _buildScheduleSlot(
            time: '11:15 - 12:30 PM',
            title: 'System Architecture Documentation',
            category: 'Research',
            priority: 'medium',
            energy: 'Moderate',
          ),
          _buildScheduleSlot(
            time: '02:00 - 03:00 PM',
            title: 'Team Sync & Standup Review',
            category: 'Work',
            priority: 'low',
            energy: 'Post-Lunch Dip',
          ),
          const SizedBox(height: 20),

          // Confirm Schedule Button
          AppButton(
            label: 'Accept & Apply Schedule to Calendar',
            icon: Icons.check,
            isFullWidth: true,
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Schedule successfully applied to Calendar!')),
              );
            },
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildScheduleSlot({
    required String time,
    required String title,
    required String category,
    required String priority,
    required String energy,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: AppCard(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  time,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.primaryViolet.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    energy,
                    style: const TextStyle(fontSize: 10, color: AppColors.primaryViolet),
                  ),
                ),
              ],
            ),
            const SizedBox(width: 14),
            Container(width: 1, height: 40, color: Colors.grey.withOpacity(0.3)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(category, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                      const SizedBox(width: 8),
                      PriorityBadge(priority: priority),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBreakSlot({required String time, required String title}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.green.withOpacity(0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.green.withOpacity(0.2)),
        ),
        child: Row(
          children: [
            const Icon(Icons.coffee_outlined, size: 18, color: Colors.green),
            const SizedBox(width: 10),
            Text(time, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.green)),
            const SizedBox(width: 10),
            Text(title, style: const TextStyle(fontSize: 11, color: Colors.green)),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 2: Weekly Planner & Workload Balancing
  // ---------------------------------------------------------------------------
  Widget _buildWeeklyPlannerTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: const [
              Text(
                'Weekly Workload Distribution',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              Text(
                'Cap: 8h/day',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildDayLoadItem(day: 'Mon', date: 'Nov 11', hours: 6.5, tasks: 5, isHeavy: false),
          _buildDayLoadItem(day: 'Tue', date: 'Nov 12', hours: 7.0, tasks: 6, isHeavy: false),
          _buildDayLoadItem(day: 'Wed', date: 'Nov 13', hours: 8.5, tasks: 7, isHeavy: true),
          _buildDayLoadItem(day: 'Thu', date: 'Nov 14', hours: 5.0, tasks: 4, isHeavy: false),
          _buildDayLoadItem(day: 'Fri', date: 'Nov 15', hours: 6.0, tasks: 5, isHeavy: false),
          _buildDayLoadItem(day: 'Sat', date: 'Nov 16', hours: 2.0, tasks: 2, isHeavy: false),
          _buildDayLoadItem(day: 'Sun', date: 'Nov 17', hours: 0.0, tasks: 0, isRest: true),
          const SizedBox(height: 20),
          AppButton(
            label: 'Balance & Redistribute Wednesday Overload',
            icon: Icons.balance,
            isFullWidth: true,
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Rebalanced: Moved 1.5h from Wednesday to Thursday!')),
              );
            },
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildDayLoadItem({
    required String day,
    required String date,
    required double hours,
    required int tasks,
    bool isHeavy = false,
    bool isRest = false,
  }) {
    final pct = (hours / 10.0).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: AppCard(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            SizedBox(
              width: 50,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(day, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  Text(date, style: const TextStyle(color: Colors.grey, fontSize: 10)),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: isRest
                  ? const Text(
                      'Rest Day 🌱',
                      style: TextStyle(color: Colors.green, fontSize: 12, fontWeight: FontWeight.w500),
                    )
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '$hours hrs • $tasks tasks',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: isHeavy ? AppColors.priorityUrgent : null,
                              ),
                            ),
                            if (isHeavy)
                              const Text(
                                'Heavy Day',
                                style: TextStyle(fontSize: 10, color: AppColors.priorityUrgent, fontWeight: FontWeight.bold),
                              ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        LinearProgressIndicator(
                          value: pct,
                          backgroundColor: Colors.grey.withOpacity(0.15),
                          valueColor: AlwaysStoppedAnimation<Color>(
                            isHeavy ? AppColors.priorityUrgent : AppColors.primaryViolet,
                          ),
                          minHeight: 6,
                        ),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: AI Assistant & Coach Chat
  // ---------------------------------------------------------------------------
  Widget _buildAssistantChatTab() {
    return Column(
      children: [
        // Suggested prompt pills
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          color: Theme.of(context).cardColor,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildPromptChip('Plan my day'),
                _buildPromptChip('What tasks are overdue?'),
                _buildPromptChip('How is my productivity?'),
                _buildPromptChip('Break down cybersecurity goal'),
              ],
            ),
          ),
        ),
        const Divider(height: 1),

        // Message List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _chatMessages.length,
            itemBuilder: (context, index) {
              final msg = _chatMessages[index];
              final isUser = msg['sender'] == 'user';
              return Align(
                alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(12),
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.8,
                  ),
                  decoration: BoxDecoration(
                    color: isUser
                        ? AppColors.primaryViolet
                        : Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(12),
                    border: isUser ? null : Border.all(color: Colors.grey.withOpacity(0.2)),
                  ),
                  child: Text(
                    msg['text']!,
                    style: TextStyle(
                      color: isUser ? Colors.white : null,
                      fontSize: 13,
                    ),
                  ),
                ),
              );
            },
          ),
        ),

        // Bottom Chat Input
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            border: Border(top: BorderSide(color: Colors.grey.withOpacity(0.2))),
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _chatController,
                  decoration: const InputDecoration(
                    hintText: 'Ask PlanWise AI...',
                    border: InputBorder.none,
                    isDense: true,
                  ),
                  onSubmitted: _sendChatMessage,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.send_rounded, color: AppColors.primaryViolet),
                onPressed: () => _sendChatMessage(_chatController.text),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPromptChip(String text) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: ActionChip(
        label: Text(text, style: const TextStyle(fontSize: 11)),
        onPressed: () => _sendChatMessage(text),
      ),
    );
  }
}

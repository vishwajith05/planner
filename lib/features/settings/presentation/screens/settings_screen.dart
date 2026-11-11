import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings & Profile'),
      ),
      body: ListView(
        children: [
          const SizedBox(height: 12),
          ListTile(
            leading: CircleAvatar(
              backgroundColor: AppColors.primary.withOpacity(0.15),
              child: const Icon(Icons.person, color: AppColors.primary),
            ),
            title: const Text('Lead Architect', style: TextStyle(fontWeight: FontWeight.bold)),
            subtitle: const Text('developer@planwise.ai'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          const Divider(height: 32),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: Text(
              'PREFERENCES',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppColors.lightTextSecondary,
                letterSpacing: 0.5,
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.palette_outlined),
            title: const Text('Theme'),
            subtitle: const Text('System Default (Light / Dark)'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.notifications_active_outlined),
            title: const Text('Notifications & Reminders'),
            subtitle: const Text('Daily briefing at 8:00 AM'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.psychology_alt_outlined),
            title: const Text('AI Assistant Provider'),
            subtitle: const Text('Deterministic Engine + Multi-Provider LLM'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.sync_outlined),
            title: const Text('Offline Mode & Sync'),
            subtitle: const Text('Local Cache Enabled'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          const Divider(height: 32),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About PlanWise AI'),
            subtitle: const Text('v1.0.0 (Phase 1 Foundation)'),
          ),
        ],
      ),
    );
  }
}

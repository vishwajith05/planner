import 'dart:async';
import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/app_card.dart';

class FocusScreen extends StatefulWidget {
  const FocusScreen({Key? key}) : super(key: key);

  @override
  State<FocusScreen> createState() => _FocusScreenState();
}

class _FocusScreenState extends State<FocusScreen> {
  static const int _defaultFocusSeconds = 25 * 60;
  static const int _defaultShortBreakSeconds = 5 * 60;
  static const int _defaultLongBreakSeconds = 15 * 60;

  int _totalSeconds = _defaultFocusSeconds;
  int _remainingSeconds = _defaultFocusSeconds;
  Timer? _timer;
  bool _isRunning = false;
  String _mode = 'focus'; // 'focus', 'short_break', 'long_break'

  int _completedSessionsToday = 3;
  int _totalFocusMinutesToday = 75;

  String _linkedTask = 'Implement FastAPI Deterministic Scheduler Engine';

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startTimer() {
    setState(() => _isRunning = true);
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingSeconds > 0) {
        setState(() => _remainingSeconds--);
      } else {
        _timer?.cancel();
        setState(() {
          _isRunning = false;
          if (_mode == 'focus') {
            _completedSessionsToday++;
            _totalFocusMinutesToday += (_totalSeconds / 60).round();
          }
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_mode == 'focus' ? 'Focus Session Completed! Take a breather.' : 'Break completed! Ready to focus?'),
            backgroundColor: AppColors.statusSuccess,
          ),
        );
      }
    });
  }

  void _pauseTimer() {
    _timer?.cancel();
    setState(() => _isRunning = false);
  }

  void _resetTimer() {
    _timer?.cancel();
    setState(() {
      _isRunning = false;
      _remainingSeconds = _totalSeconds;
    });
  }

  void _setMode(String mode) {
    _timer?.cancel();
    setState(() {
      _mode = mode;
      _isRunning = false;
      if (mode == 'focus') {
        _totalSeconds = _defaultFocusSeconds;
      } else if (mode == 'short_break') {
        _totalSeconds = _defaultShortBreakSeconds;
      } else {
        _totalSeconds = _defaultLongBreakSeconds;
      }
      _remainingSeconds = _totalSeconds;
    });
  }

  String _formatTime(int sec) {
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    final progress = _totalSeconds > 0 ? (_totalSeconds - _remainingSeconds) / _totalSeconds : 0.0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Focus & Pomodoro Timer'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          children: [
            // Mode Selector
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'focus', label: Text('Focus (25m)')),
                ButtonSegment(value: 'short_break', label: Text('Short (5m)')),
                ButtonSegment(value: 'long_break', label: Text('Long (15m)')),
              ],
              selected: {_mode},
              onSelectionChanged: (val) => _setMode(val.first),
            ),
            const SizedBox(height: 20),

            // Linked Task Pill
            AppCard(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.bolt, color: AppColors.accent, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Target: $_linkedTask',
                      style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 36),

            // Circular Countdown Display
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 240,
                  height: 240,
                  child: CircularProgressIndicator(
                    value: 1.0 - progress,
                    strokeWidth: 10,
                    backgroundColor: AppColors.lightBorder,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _mode == 'focus' ? AppColors.primary : AppColors.statusSuccess,
                    ),
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _formatTime(_remainingSeconds),
                      style: const TextStyle(fontSize: 54, fontWeight: FontWeight.bold, letterSpacing: -1),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _mode == 'focus'
                          ? (_isRunning ? 'DEEP WORK' : 'READY')
                          : 'REST & RECHARGE',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.5,
                        color: _mode == 'focus' ? AppColors.primary : AppColors.statusSuccess,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 40),

            // Control Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                OutlinedButton.icon(
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reset'),
                  onPressed: _resetTimer,
                ),
                const SizedBox(width: 16),
                AppButton(
                  icon: _isRunning ? Icons.pause : Icons.play_arrow,
                  label: _isRunning ? 'Pause' : 'Start Focus',
                  onPressed: _isRunning ? _pauseTimer : _startTimer,
                ),
              ],
            ),
            const SizedBox(height: 36),

            // Today's Focus Stats Row
            AppCard(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      Text('$_totalFocusMinutesToday mins', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 2),
                      const Text('Today\'s Focus Time', style: TextStyle(fontSize: 11, color: AppColors.lightTextSecondary)),
                    ],
                  ),
                  Container(width: 1, height: 32, color: AppColors.lightBorder),
                  Column(
                    children: [
                      Text('$_completedSessionsToday', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 2),
                      const Text('Sessions Completed', style: TextStyle(fontSize: 11, color: AppColors.lightTextSecondary)),
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
}

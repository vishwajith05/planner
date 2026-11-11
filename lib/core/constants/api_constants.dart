class ApiConstants {
  // Configurable base URL: default to local FastAPI backend
  // For physical Android device debugging: replace with your local LAN IP (e.g. 192.168.1.x:8000)
  // For Android emulator: http://10.0.2.2:8000
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';

  static const String healthEndpoint = '/health';
  static const String dashboardEndpoint = '/dashboard/summary';
  static const String tasksEndpoint = '/tasks';
  static const String aiScheduleEndpoint = '/ai/schedule';
  static const String habitsEndpoint = '/habits';
  static const String focusEndpoint = '/focus';
  static const String goalsEndpoint = '/goals';
  static const String analyticsEndpoint = '/analytics';
}

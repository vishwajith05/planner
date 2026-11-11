import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../domain/task_model.dart';
import '../../../shared/models/priority.dart';

class TaskRepository {
  final ApiClient client;

  // Local fallback cache for offline resiliency
  final List<TaskModel> _localTasks = [
    TaskModel(
      id: 'task-1',
      title: 'Review Cybersecurity Network Security Architecture',
      description: 'Audit firewall rules and verify Zero Trust boundaries',
      priority: TaskPriority.urgent,
      category: 'Cybersecurity',
      tags: 'security,network',
      estimatedMinutes: 90,
      isCompleted: true,
      subtasks: const [
        SubtaskModel(id: 's1', title: 'Port scan audit', isCompleted: true),
        SubtaskModel(id: 's2', title: 'WAF rules inspection', isCompleted: true),
      ],
    ),
    TaskModel(
      id: 'task-2',
      title: 'Implement FastAPI Deterministic Scheduler Engine',
      description: 'Deterministic slot allocation with no overlaps and energy curves',
      priority: TaskPriority.high,
      category: 'Programming',
      tags: 'fastapi,python,ai',
      estimatedMinutes: 60,
      isCompleted: false,
      subtasks: const [
        SubtaskModel(id: 's3', title: 'Slot constraint algorithm', isCompleted: true),
        SubtaskModel(id: 's4', title: 'Energy-pacing tests', isCompleted: false),
      ],
    ),
    TaskModel(
      id: 'task-3',
      title: 'Deep Work: Flutter State Management & Clean Architecture',
      description: 'Riverpod Notifier implementation and GoRouter deep linking',
      priority: TaskPriority.medium,
      category: 'Education',
      tags: 'flutter,riverpod',
      estimatedMinutes: 90,
      isCompleted: false,
    ),
    TaskModel(
      id: 'task-4',
      title: 'Evening Physical Conditioning & Hydration',
      description: 'Cardio training and mobility session',
      priority: TaskPriority.low,
      category: 'Health',
      tags: 'fitness,health',
      estimatedMinutes: 45,
      isCompleted: false,
    ),
  ];

  TaskRepository({ApiClient? client}) : client = client ?? apiClient;

  Future<List<TaskModel>> getTasks({
    String? category,
    String? priority,
    String? status,
    bool? isCompleted,
    String? search,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (category != null && category.isNotEmpty) queryParams['category'] = category;
      if (priority != null && priority.isNotEmpty) queryParams['priority'] = priority;
      if (status != null && status.isNotEmpty) queryParams['status'] = status;
      if (isCompleted != null) queryParams['is_completed'] = isCompleted;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final res = await client.dio.get('/tasks', queryParameters: queryParams);
      if (res.statusCode == 200) {
        final list = (res.data as List<dynamic>)
            .map((e) => TaskModel.fromJson(e as Map<String, dynamic>))
            .toList();
        return list;
      }
    } catch (_) {
      // Offline fallback: filter local in-memory tasks
    }

    var filtered = List<TaskModel>.from(_localTasks);
    if (category != null && category.isNotEmpty) {
      filtered = filtered.where((t) => t.category.toLowerCase() == category.toLowerCase()).toList();
    }
    if (priority != null && priority.isNotEmpty) {
      filtered = filtered.where((t) => t.priority.name.toLowerCase() == priority.toLowerCase()).toList();
    }
    if (isCompleted != null) {
      filtered = filtered.where((t) => t.isCompleted == isCompleted).toList();
    }
    if (search != null && search.isNotEmpty) {
      final q = search.toLowerCase();
      filtered = filtered.where((t) =>
          t.title.toLowerCase().contains(q) ||
          (t.description?.toLowerCase().contains(q) ?? false) ||
          t.tags.toLowerCase().contains(q)).toList();
    }
    return filtered;
  }

  Future<TaskModel> createTask(TaskModel task) async {
    try {
      final res = await client.dio.post('/tasks', data: task.toJson());
      if (res.statusCode == 201) {
        final created = TaskModel.fromJson(res.data as Map<String, dynamic>);
        _localTasks.insert(0, created);
        return created;
      }
    } catch (_) {
      // Local fallback
    }
    _localTasks.insert(0, task);
    return task;
  }

  Future<TaskModel> toggleTask(String taskId) async {
    try {
      final res = await client.dio.post('/tasks/$taskId/toggle');
      if (res.statusCode == 200) {
        final updated = TaskModel.fromJson(res.data as Map<String, dynamic>);
        final idx = _localTasks.indexWhere((t) => t.id == taskId);
        if (idx != -1) _localTasks[idx] = updated;
        return updated;
      }
    } catch (_) {}

    final idx = _localTasks.indexWhere((t) => t.id == taskId);
    if (idx != -1) {
      final t = _localTasks[idx];
      final updated = t.copyWith(isCompleted: !t.isCompleted, status: !t.isCompleted ? 'completed' : 'in_progress');
      _localTasks[idx] = updated;
      return updated;
    }
    throw Exception('Task not found');
  }

  Future<void> deleteTask(String taskId) async {
    try {
      await client.dio.delete('/tasks/$taskId');
    } catch (_) {}
    _localTasks.removeWhere((t) => t.id == taskId);
  }

  Future<TaskModel> duplicateTask(String taskId) async {
    try {
      final res = await client.dio.post('/tasks/$taskId/duplicate');
      if (res.statusCode == 201) {
        final dup = TaskModel.fromJson(res.data as Map<String, dynamic>);
        _localTasks.insert(0, dup);
        return dup;
      }
    } catch (_) {}

    final original = _localTasks.firstWhere((t) => t.id == taskId);
    final dup = original.copyWith(
      id: 'task-${DateTime.now().millisecondsSinceEpoch}',
      title: 'Copy of ${original.title}',
      isCompleted: false,
    );
    _localTasks.insert(0, dup);
    return dup;
  }
}

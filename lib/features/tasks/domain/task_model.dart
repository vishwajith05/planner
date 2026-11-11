import '../../../shared/models/priority.dart';

class SubtaskModel {
  final String id;
  final String title;
  final bool isCompleted;

  const SubtaskModel({
    required this.id,
    required this.title,
    this.isCompleted = false,
  });

  SubtaskModel copyWith({String? id, String? title, bool? isCompleted}) {
    return SubtaskModel(
      id: id ?? this.id,
      title: title ?? this.title,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'is_completed': isCompleted,
  };

  factory SubtaskModel.fromJson(Map<String, dynamic> json) {
    return SubtaskModel(
      id: json['id'] as String,
      title: json['title'] as String,
      isCompleted: json['is_completed'] as bool? ?? false,
    );
  }
}

class CategoryModel {
  final String id;
  final String name;
  final String color;
  final String icon;
  final bool isDefault;

  const CategoryModel({
    required this.id,
    required this.name,
    this.color = '#6366F1',
    this.icon = 'folder',
    this.isDefault = false,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id'] as String,
      name: json['name'] as String,
      color: json['color'] as String? ?? '#6366F1',
      icon: json['icon'] as String? ?? 'folder',
      isDefault: json['is_default'] as bool? ?? false,
    );
  }
}

class TaskModel {
  final String id;
  final String title;
  final String? description;
  final String? notes;
  final TaskPriority priority;
  final String status;
  final String category;
  final String tags;
  final String listName;
  final int estimatedMinutes;
  final int actualMinutes;
  final DateTime? startTime;
  final DateTime? dueDate;
  final DateTime? reminderTime;
  final String recurrence;
  final List<SubtaskModel> subtasks;
  final bool isCompleted;
  final DateTime? completedAt;

  const TaskModel({
    required this.id,
    required this.title,
    this.description,
    this.notes,
    this.priority = TaskPriority.medium,
    this.status = 'not_started',
    this.category = 'Personal',
    this.tags = '',
    this.listName = 'Inbox',
    this.estimatedMinutes = 30,
    this.actualMinutes = 0,
    this.startTime,
    this.dueDate,
    this.reminderTime,
    this.recurrence = 'none',
    this.subtasks = const [],
    this.isCompleted = false,
    this.completedAt,
  });

  TaskModel copyWith({
    String? id,
    String? title,
    String? description,
    String? notes,
    TaskPriority? priority,
    String? status,
    String? category,
    String? tags,
    String? listName,
    int? estimatedMinutes,
    int? actualMinutes,
    DateTime? startTime,
    DateTime? dueDate,
    DateTime? reminderTime,
    String? recurrence,
    List<SubtaskModel>? subtasks,
    bool? isCompleted,
    DateTime? completedAt,
  }) {
    return TaskModel(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      notes: notes ?? this.notes,
      priority: priority ?? this.priority,
      status: status ?? this.status,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      listName: listName ?? this.listName,
      estimatedMinutes: estimatedMinutes ?? this.estimatedMinutes,
      actualMinutes: actualMinutes ?? this.actualMinutes,
      startTime: startTime ?? this.startTime,
      dueDate: dueDate ?? this.dueDate,
      reminderTime: reminderTime ?? this.reminderTime,
      recurrence: recurrence ?? this.recurrence,
      subtasks: subtasks ?? this.subtasks,
      isCompleted: isCompleted ?? this.isCompleted,
      completedAt: completedAt ?? this.completedAt,
    );
  }

  Map<String, dynamic> toJson() => {
    'title': title,
    'description': description,
    'notes': notes,
    'priority': priority.name,
    'status': status,
    'category': category,
    'tags': tags,
    'list_name': listName,
    'estimated_minutes': estimatedMinutes,
    'actual_minutes': actualMinutes,
    'start_time': startTime?.toIso8601String(),
    'due_date': dueDate?.toIso8601String(),
    'reminder_time': reminderTime?.toIso8601String(),
    'recurrence': recurrence,
    'subtasks': subtasks.map((s) => s.toJson()).toList(),
    'is_completed': isCompleted,
  };

  factory TaskModel.fromJson(Map<String, dynamic> json) {
    return TaskModel(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      notes: json['notes'] as String?,
      priority: TaskPriority.fromString(json['priority'] as String?),
      status: json['status'] as String? ?? 'not_started',
      category: json['category'] as String? ?? 'Personal',
      tags: json['tags'] as String? ?? '',
      listName: json['list_name'] as String? ?? 'Inbox',
      estimatedMinutes: json['estimated_minutes'] as int? ?? 30,
      actualMinutes: json['actual_minutes'] as int? ?? 0,
      startTime: json['start_time'] != null ? DateTime.parse(json['start_time']) : null,
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date']) : null,
      reminderTime: json['reminder_time'] != null ? DateTime.parse(json['reminder_time']) : null,
      recurrence: json['recurrence'] as String? ?? 'none',
      subtasks: (json['subtasks'] as List<dynamic>?)
              ?.map((s) => SubtaskModel.fromJson(s as Map<String, dynamic>))
              .toList() ??
          [],
      isCompleted: json['is_completed'] as bool? ?? false,
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
    );
  }
}

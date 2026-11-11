import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/task_model.dart';
import '../../data/task_repository.dart';
import '../../../../shared/models/priority.dart';

class TaskState {
  final List<TaskModel> tasks;
  final bool isLoading;
  final String? errorMessage;
  final String? selectedCategory;
  final TaskPriority? selectedPriority;
  final String filterStatus; // 'all', 'pending', 'completed'
  final String searchQuery;

  const TaskState({
    this.tasks = const [],
    this.isLoading = false,
    this.errorMessage,
    this.selectedCategory,
    this.selectedPriority,
    this.filterStatus = 'all',
    this.searchQuery = '',
  });

  TaskState copyWith({
    List<TaskModel>? tasks,
    bool? isLoading,
    String? errorMessage,
    String? selectedCategory,
    TaskPriority? selectedPriority,
    String? filterStatus,
    String? searchQuery,
    bool clearCategory = false,
    bool clearPriority = false,
  }) {
    return TaskState(
      tasks: tasks ?? this.tasks,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      selectedCategory: clearCategory ? null : (selectedCategory ?? this.selectedCategory),
      selectedPriority: clearPriority ? null : (selectedPriority ?? this.selectedPriority),
      filterStatus: filterStatus ?? this.filterStatus,
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }

  int get totalCount => tasks.length;
  int get completedCount => tasks.where((t) => t.isCompleted).length;
  int get pendingCount => tasks.where((t) => !t.isCompleted).length;
}

class TaskNotifier extends StateNotifier<TaskState> {
  final TaskRepository repository;

  TaskNotifier(this.repository) : super(const TaskState()) {
    loadTasks();
  }

  Future<void> loadTasks() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      bool? isCompleted;
      if (state.filterStatus == 'pending') isCompleted = false;
      if (state.filterStatus == 'completed') isCompleted = true;

      final tasks = await repository.getTasks(
        category: state.selectedCategory,
        priority: state.selectedPriority?.name,
        isCompleted: isCompleted,
        search: state.searchQuery,
      );
      state = state.copyWith(tasks: tasks, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.toString());
    }
  }

  Future<void> addTask(TaskModel task) async {
    state = state.copyWith(isLoading: true);
    try {
      await repository.createTask(task);
      await loadTasks();
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.toString());
    }
  }

  Future<void> toggleTask(String taskId) async {
    try {
      await repository.toggleTask(taskId);
      await loadTasks();
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
    }
  }

  Future<void> deleteTask(String taskId) async {
    try {
      await repository.deleteTask(taskId);
      await loadTasks();
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
    }
  }

  Future<void> duplicateTask(String taskId) async {
    try {
      await repository.duplicateTask(taskId);
      await loadTasks();
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
    }
  }

  void setFilterStatus(String status) {
    state = state.copyWith(filterStatus: status);
    loadTasks();
  }

  void setCategory(String? category) {
    if (state.selectedCategory == category) {
      state = state.copyWith(clearCategory: true);
    } else {
      state = state.copyWith(selectedCategory: category);
    }
    loadTasks();
  }

  void setPriority(TaskPriority? priority) {
    if (state.selectedPriority == priority) {
      state = state.copyWith(clearPriority: true);
    } else {
      state = state.copyWith(selectedPriority: priority);
    }
    loadTasks();
  }

  void setSearchQuery(String query) {
    state = state.copyWith(searchQuery: query);
    loadTasks();
  }
}

final taskRepositoryProvider = Provider<TaskRepository>((ref) => TaskRepository());

final taskNotifierProvider = StateNotifierProvider<TaskNotifier, TaskState>((ref) {
  final repo = ref.watch(taskRepositoryProvider);
  return TaskNotifier(repo);
});

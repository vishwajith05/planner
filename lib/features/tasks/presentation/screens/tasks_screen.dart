import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/priority_badge.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../shared/models/priority.dart';
import '../state/task_provider.dart';
import '../widgets/create_task_sheet.dart';
import '../../domain/task_model.dart';

class TasksScreen extends ConsumerStatefulWidget {
  const TasksScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends ConsumerState<TasksScreen> {
  final TextEditingController _quickAddController = TextEditingController();
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;

  final List<String> _categories = [
    'All',
    'Programming',
    'Cybersecurity',
    'Work',
    'Education',
    'Personal',
    'Health',
    'Research',
  ];

  @override
  void dispose() {
    _quickAddController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _handleQuickAdd() {
    final text = _quickAddController.text.trim();
    if (text.isNotEmpty) {
      final task = TaskModel(
        id: 'task-${DateTime.now().millisecondsSinceEpoch}',
        title: text,
        category: 'Personal',
        priority: TaskPriority.medium,
        estimatedMinutes: 30,
      );
      ref.read(taskNotifierProvider.notifier).addTask(task);
      _quickAddController.clear();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Task "$text" created'),
          action: SnackBarAction(label: 'UNDO', onPressed: () {}),
        ),
      );
    }
  }

  void _openCreateTaskSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => CreateTaskSheet(
        onTaskCreated: (task) {
          ref.read(taskNotifierProvider.notifier).addTask(task);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final taskState = ref.watch(taskNotifierProvider);
    final notifier = ref.read(taskNotifierProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: _isSearching
            ? TextField(
                controller: _searchController,
                autofocus: true,
                decoration: InputDecoration(
                  hintText: 'Search tasks, tags, notes...',
                  border: InputBorder.none,
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      _searchController.clear();
                      notifier.setSearchQuery('');
                      setState(() => _isSearching = false);
                    },
                  ),
                ),
                onChanged: (val) => notifier.setSearchQuery(val),
              )
            : const Text('Tasks & Focus Lists'),
        actions: [
          IconButton(
            icon: Icon(_isSearching ? Icons.close : Icons.search),
            onPressed: () {
              setState(() {
                _isSearching = !_isSearching;
                if (!_isSearching) {
                  _searchController.clear();
                  notifier.setSearchQuery('');
                }
              });
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            onSelected: (val) {
              // Sorting options
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'due', child: Text('Sort by Due Date')),
              const PopupMenuItem(value: 'priority', child: Text('Sort by Priority')),
              const PopupMenuItem(value: 'title', child: Text('Sort by Title')),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => notifier.loadTasks(),
        child: Column(
          children: [
            // Quick Add Input Box
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
              child: AppCard(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                child: Row(
                  children: [
                    const Icon(Icons.add_circle_outline, color: AppColors.primary),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextField(
                        controller: _quickAddController,
                        decoration: const InputDecoration(
                          hintText: 'Quick Add: "Study Python tomorrow at 6 AM"',
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.zero,
                        ),
                        onSubmitted: (_) => _handleQuickAdd(),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.arrow_upward_rounded, color: AppColors.primary),
                      onPressed: _handleQuickAdd,
                    ),
                  ],
                ),
              ),
            ),

            // Status Tabs (All, Pending, Completed)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 6.0),
              child: Row(
                children: [
                  _StatusPill(
                    label: 'All (${taskState.totalCount})',
                    isSelected: taskState.filterStatus == 'all',
                    onTap: () => notifier.setFilterStatus('all'),
                  ),
                  const SizedBox(width: 8),
                  _StatusPill(
                    label: 'Pending (${taskState.pendingCount})',
                    isSelected: taskState.filterStatus == 'pending',
                    onTap: () => notifier.setFilterStatus('pending'),
                  ),
                  const SizedBox(width: 8),
                  _StatusPill(
                    label: 'Done (${taskState.completedCount})',
                    isSelected: taskState.filterStatus == 'completed',
                    onTap: () => notifier.setFilterStatus('completed'),
                  ),
                ],
              ),
            ),

            // Category Chips Row
            SizedBox(
              height: 38,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: _categories.length,
                itemBuilder: (context, index) {
                  final cat = _categories[index];
                  final isAll = cat == 'All';
                  final isSelected = isAll
                      ? taskState.selectedCategory == null
                      : taskState.selectedCategory == cat;

                  return Padding(
                    padding: const EdgeInsets.only(right: 6.0),
                    child: FilterChip(
                      label: Text(cat, style: const TextStyle(fontSize: 12)),
                      selected: isSelected,
                      selectedColor: AppColors.primary.withOpacity(0.18),
                      showCheckmark: false,
                      onSelected: (_) {
                        notifier.setCategory(isAll ? null : cat);
                      },
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 6),

            // Tasks List
            Expanded(
              child: taskState.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : taskState.tasks.isEmpty
                      ? EmptyStateWidget(
                          icon: Icons.checklist_rtl_rounded,
                          title: 'No Tasks Found',
                          message: taskState.searchQuery.isNotEmpty
                              ? 'No results matched "${taskState.searchQuery}"'
                              : 'You have no tasks in this view. Enjoy the free time or add one!',
                          actionLabel: 'Create Task',
                          onAction: _openCreateTaskSheet,
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.fromLTRB(16, 4, 16, 80),
                          itemCount: taskState.tasks.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (context, index) {
                            final task = taskState.tasks[index];
                            final completedSubtasks = task.subtasks.where((s) => s.isCompleted).length;

                            return AppCard(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Checkbox(
                                    value: task.isCompleted,
                                    activeColor: AppColors.primary,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    onChanged: (_) => notifier.toggleTask(task.id),
                                  ),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          task.title,
                                          style: TextStyle(
                                            fontSize: 14.5,
                                            fontWeight: FontWeight.w600,
                                            decoration: task.isCompleted ? TextDecoration.lineThrough : null,
                                            color: task.isCompleted ? AppColors.lightTextSecondary : null,
                                          ),
                                        ),
                                        if (task.description != null && task.description!.isNotEmpty) ...[
                                          const SizedBox(height: 3),
                                          Text(
                                            task.description!,
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: AppColors.lightTextSecondary,
                                            ),
                                          ),
                                        ],
                                        const SizedBox(height: 6),
                                        Wrap(
                                          spacing: 6,
                                          runSpacing: 4,
                                          crossAxisAlignment: WrapCrossAlignment.center,
                                          children: [
                                            // Category Pill
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: AppColors.lightBorder.withOpacity(0.4),
                                                borderRadius: BorderRadius.circular(4),
                                              ),
                                              child: Text(
                                                task.category,
                                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
                                              ),
                                            ),
                                            // Duration
                                            Row(
                                              mainAxisSize: MainAxisSize.min,
                                              children: [
                                                const Icon(Icons.timer_outlined, size: 12, color: AppColors.lightTextSecondary),
                                                const SizedBox(width: 3),
                                                Text(
                                                  '${task.estimatedMinutes}m',
                                                  style: const TextStyle(fontSize: 11, color: AppColors.lightTextSecondary),
                                                ),
                                              ],
                                            ),
                                            // Subtasks indicator
                                            if (task.subtasks.isNotEmpty) ...[
                                              Row(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  const Icon(Icons.check_box_outlined, size: 12, color: AppColors.lightTextSecondary),
                                                  const SizedBox(width: 3),
                                                  Text(
                                                    '$completedSubtasks/${task.subtasks.length}',
                                                    style: const TextStyle(fontSize: 11, color: AppColors.lightTextSecondary),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      PriorityBadge(priority: task.priority),
                                      PopupMenuButton<String>(
                                        icon: const Icon(Icons.more_vert, size: 18, color: AppColors.lightTextSecondary),
                                        padding: EdgeInsets.zero,
                                        onSelected: (val) {
                                          if (val == 'toggle') notifier.toggleTask(task.id);
                                          if (val == 'duplicate') notifier.duplicateTask(task.id);
                                          if (val == 'delete') notifier.deleteTask(task.id);
                                        },
                                        itemBuilder: (_) => [
                                          PopupMenuItem(
                                            value: 'toggle',
                                            child: Text(task.isCompleted ? 'Mark Pending' : 'Mark Completed'),
                                          ),
                                          const PopupMenuItem(
                                            value: 'duplicate',
                                            child: Text('Duplicate Task'),
                                          ),
                                          const PopupMenuItem(
                                            value: 'delete',
                                            child: Text('Delete Task', style: TextStyle(color: AppColors.statusError)),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('Add Task'),
        onPressed: _openCreateTaskSheet,
      ),
    );
  }
}

class _StatusPill extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _StatusPill({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primary : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected ? AppColors.primary : AppColors.lightBorder,
            ),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                color: isSelected ? Colors.white : AppColors.lightTextSecondary,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

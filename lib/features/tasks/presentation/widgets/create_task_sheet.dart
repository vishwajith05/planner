import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../shared/models/priority.dart';
import '../../domain/task_model.dart';

class CreateTaskSheet extends StatefulWidget {
  final Function(TaskModel task) onTaskCreated;

  const CreateTaskSheet({Key? key, required this.onTaskCreated}) : super(key: key);

  @override
  State<CreateTaskSheet> createState() => _CreateTaskSheetState();
}

class _CreateTaskSheetState extends State<CreateTaskSheet> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _notesController = TextEditingController();
  final _subtaskInputController = TextEditingController();

  String _selectedCategory = 'Programming';
  TaskPriority _selectedPriority = TaskPriority.medium;
  int _estimatedMinutes = 45;
  final List<SubtaskModel> _subtasks = [];

  final List<String> _categories = [
    'Programming',
    'Cybersecurity',
    'Work',
    'Education',
    'Personal',
    'Research',
    'Health',
  ];

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _notesController.dispose();
    _subtaskInputController.dispose();
    super.dispose();
  }

  void _addSubtask() {
    final text = _subtaskInputController.text.trim();
    if (text.isNotEmpty) {
      setState(() {
        _subtasks.add(
          SubtaskModel(
            id: 'sub-${DateTime.now().millisecondsSinceEpoch}',
            title: text,
            isCompleted: false,
          ),
        );
        _subtaskInputController.clear();
      });
    }
  }

  void _submit() {
    if (_formKey.currentState?.validate() ?? false) {
      final task = TaskModel(
        id: 'task-${DateTime.now().millisecondsSinceEpoch}',
        title: _titleController.text.trim(),
        description: _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        notes: _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
        category: _selectedCategory,
        priority: _selectedPriority,
        estimatedMinutes: _estimatedMinutes,
        subtasks: List.from(_subtasks),
        isCompleted: false,
      );
      widget.onTaskCreated(task);
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: EdgeInsets.fromLTRB(20, 16, 20, 16 + bottomInset),
      child: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.lightBorder,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Create New Task',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Title input
              TextFormField(
                controller: _titleController,
                autofocus: true,
                decoration: const InputDecoration(
                  labelText: 'Task Title *',
                  hintText: 'e.g. Implement zero-trust network policy',
                ),
                validator: (val) => (val == null || val.trim().isEmpty) ? 'Please enter a task title' : null,
              ),
              const SizedBox(height: 12),

              // Description input
              TextFormField(
                controller: _descriptionController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: 'Description (Optional)',
                  hintText: 'Add context, scope, or requirements',
                ),
              ),
              const SizedBox(height: 14),

              // Category Selector
              const Text('Category', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: _categories.map((cat) {
                    final isSel = _selectedCategory == cat;
                    return Padding(
                      padding: const EdgeInsets.only(right: 6.0),
                      child: ChoiceChip(
                        label: Text(cat),
                        selected: isSel,
                        selectedColor: AppColors.primary.withOpacity(0.2),
                        onSelected: (selected) {
                          if (selected) setState(() => _selectedCategory = cat);
                        },
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 14),

              // Priority Selector
              const Text('Priority Level', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              Row(
                children: TaskPriority.values.map((p) {
                  final isSel = _selectedPriority == p;
                  return Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2.0),
                      child: InkWell(
                        onTap: () => setState(() => _selectedPriority = p),
                        borderRadius: BorderRadius.circular(8),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: isSel ? p.color.withOpacity(0.2) : Colors.transparent,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: isSel ? p.color : AppColors.lightBorder,
                              width: isSel ? 2 : 1,
                            ),
                          ),
                          child: Center(
                            child: Text(
                              p.label,
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: isSel ? FontWeight.bold : FontWeight.w500,
                                color: isSel ? p.color : null,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 14),

              // Estimated Duration Slider
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Estimated Duration', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  Text(
                    '$_estimatedMinutes mins',
                    style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary),
                  ),
                ],
              ),
              Slider(
                value: _estimatedMinutes.toDouble(),
                min: 15,
                max: 180,
                divisions: 11,
                label: '$_estimatedMinutes mins',
                onChanged: (val) => setState(() => _estimatedMinutes = val.round()),
              ),
              const SizedBox(height: 10),

              // Subtasks Checklist
              const Text('Subtasks & Milestones', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _subtaskInputController,
                      decoration: const InputDecoration(
                        hintText: 'Add subtask...',
                        isDense: true,
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                      onSubmitted: (_) => _addSubtask(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filledTonal(
                    icon: const Icon(Icons.add),
                    onPressed: _addSubtask,
                  ),
                ],
              ),
              if (_subtasks.isNotEmpty) ...[
                const SizedBox(height: 8),
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _subtasks.length,
                  itemBuilder: (context, index) {
                    final item = _subtasks[index];
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 2.0),
                      child: Row(
                        children: [
                          const Icon(Icons.check_box_outline_blank, size: 16, color: AppColors.lightTextSecondary),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(item.title, style: const TextStyle(fontSize: 13)),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, size: 16, color: AppColors.statusError),
                            onPressed: () {
                              setState(() => _subtasks.removeAt(index));
                            },
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
              const SizedBox(height: 18),

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: AppButton(
                      label: 'Save Task',
                      onPressed: _submit,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

import 'dart:convert';
import 'package:uuid/uuid.dart';
import '../storage/local_storage.dart';

enum SyncAction { create, update, delete, toggle }

class SyncMutation {
  final String id;
  final String entityType; // 'task', 'habit', 'focus'
  final SyncAction action;
  final String entityId;
  final Map<String, dynamic>? data;
  final DateTime clientTimestamp;

  SyncMutation({
    String? id,
    required this.entityType,
    required this.action,
    required this.entityId,
    this.data,
    DateTime? clientTimestamp,
  })  : id = id ?? const Uuid().v4(),
        clientTimestamp = clientTimestamp ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'id': id,
        'entity_type': entityType,
        'action': action.name,
        'entity_id': entityId,
        'data': data,
        'client_timestamp': clientTimestamp.toIso8601String(),
      };

  factory SyncMutation.fromJson(Map<String, dynamic> json) => SyncMutation(
        id: json['id'] as String,
        entityType: json['entity_type'] as String,
        action: SyncAction.values.firstWhere(
          (e) => e.name == json['action'],
          orElse: () => SyncAction.update,
        ),
        entityId: json['entity_id'] as String,
        data: json['data'] as Map<String, dynamic>?,
        clientTimestamp: DateTime.parse(json['client_timestamp'] as String),
      );
}

class SyncQueue {
  static const String _queueStorageKey = 'planwise_sync_queue_v1';
  final List<SyncMutation> _pendingMutations = [];

  List<SyncMutation> get pendingMutations => List.unmodifiable(_pendingMutations);

  bool get hasPendingMutations => _pendingMutations.isNotEmpty;

  int get pendingCount => _pendingMutations.length;

  Future<void> init() async {
    final storage = await LocalStorage.getInstance();
    final list = storage.getJsonList(_queueStorageKey);
    _pendingMutations.clear();
    for (final item in list) {
      _pendingMutations.add(SyncMutation.fromJson(item));
    }
  }

  Future<void> enqueue(SyncMutation mutation) async {
    _pendingMutations.add(mutation);
    await _persist();
  }

  Future<void> remove(String mutationId) async {
    _pendingMutations.removeWhere((m) => m.id == mutationId);
    await _persist();
  }

  Future<void> clear() async {
    _pendingMutations.clear();
    await _persist();
  }

  Future<void> _persist() async {
    final storage = await LocalStorage.getInstance();
    final jsonList = _pendingMutations.map((m) => m.toJson()).toList();
    await storage.setJsonList(_queueStorageKey, jsonList);
  }
}

final syncQueue = SyncQueue();

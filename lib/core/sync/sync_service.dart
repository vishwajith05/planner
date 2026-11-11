import 'package:dio/dio.dart';
import '../network/api_client.dart';
import '../storage/local_storage.dart';
import 'sync_queue.dart';

class SyncService {
  final ApiClient client;
  final SyncQueue queue;
  static const String _lastSyncedAtKey = 'planwise_last_synced_at';

  bool _isSyncing = false;
  bool get isSyncing => _isSyncing;

  SyncService({ApiClient? client, SyncQueue? queue})
      : client = client ?? apiClient,
        queue = queue ?? syncQueue;

  Future<DateTime?> getLastSyncedAt() async {
    final storage = await LocalStorage.getInstance();
    final str = storage.getString(_lastSyncedAtKey);
    return str != null ? DateTime.tryParse(str) : null;
  }

  Future<void> setLastSyncedAt(DateTime timestamp) async {
    final storage = await LocalStorage.getInstance();
    await storage.setString(_lastSyncedAtKey, timestamp.toIso8601String());
  }

  /// Pushes all offline queued mutations and downloads delta changes since last sync.
  Future<bool> synchronize() async {
    if (_isSyncing) return false;
    _isSyncing = true;

    try {
      await queue.init();
      final lastSync = await getLastSyncedAt();
      final mutations = queue.pendingMutations;

      final payload = {
        'last_synced_at': lastSync?.toIso8601String(),
        'mutations': mutations.map((m) => m.toJson()).toList(),
      };

      final response = await client.dio.post('/sync/full', data: payload);

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;

        // Clear successfully pushed mutations
        await queue.clear();

        // Save server timestamp as new last synced checkpoint
        final pushResults = data['push_results'] as Map<String, dynamic>;
        final serverTimestampStr = pushResults['server_timestamp'] as String;
        final serverTime = DateTime.parse(serverTimestampStr);
        await setLastSyncedAt(serverTime);

        return true;
      }
      return false;
    } catch (_) {
      // Network failure or offline; queue remains safely preserved on device
      return false;
    } finally {
      _isSyncing = false;
    }
  }
}

final syncService = SyncService();

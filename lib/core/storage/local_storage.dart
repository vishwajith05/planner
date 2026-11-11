import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// Lightweight persistent local storage wrapper for offline capability.
class LocalStorage {
  static LocalStorage? _instance;
  static SharedPreferences? _prefs;

  LocalStorage._();

  static Future<LocalStorage> getInstance() async {
    if (_instance == null) {
      _instance = LocalStorage._();
      _prefs = await SharedPreferences.getInstance();
    }
    return _instance!;
  }

  // Generic String
  Future<bool> setString(String key, String value) async {
    return await _prefs?.setString(key, value) ?? false;
  }

  String? getString(String key) {
    return _prefs?.getString(key);
  }

  // JSON objects
  Future<bool> setJson(String key, Map<String, dynamic> json) async {
    return await setString(key, jsonEncode(json));
  }

  Map<String, dynamic>? getJson(String key) {
    final str = getString(key);
    if (str == null) return null;
    try {
      return jsonDecode(str) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  // JSON lists
  Future<bool> setJsonList(String key, List<Map<String, dynamic>> list) async {
    return await setString(key, jsonEncode(list));
  }

  List<Map<String, dynamic>> getJsonList(String key) {
    final str = getString(key);
    if (str == null) return [];
    try {
      final decoded = jsonDecode(str) as List<dynamic>;
      return decoded.map((e) => e as Map<String, dynamic>).toList();
    } catch (_) {
      return [];
    }
  }

  Future<bool> remove(String key) async {
    return await _prefs?.remove(key) ?? false;
  }

  Future<bool> clear() async {
    return await _prefs?.clear() ?? false;
  }
}

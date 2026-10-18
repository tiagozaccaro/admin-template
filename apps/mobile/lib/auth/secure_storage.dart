// Secure storage for OAuth tokens.
//
// Production backing is [flutter_secure_storage] (iOS Keychain / Android
// EncryptedSharedPreferences). An in-memory implementation remains available
// for tests and for environments where secure storage is unavailable.
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

abstract class SecureStorage {
  /// Read a value by key, or null when absent.
  Future<String?> read(String key);

  /// Write a value by key.
  Future<void> write(String key, String value);

  /// Delete a value by key.
  Future<void> delete(String key);
}

/// In-memory secure storage. Tokens live only in RAM and are lost when the
/// process restarts -- no long-lived on-device tokens.
class InMemorySecureStorage implements SecureStorage {
  final Map<String, String> _store = <String, String>{};

  @override
  Future<String?> read(String key) async => _store[key];

  @override
  Future<void> write(String key, String value) async {
    _store[key] = value;
  }

  @override
  Future<void> delete(String key) async => _store.remove(key);
}

/// Secure storage backed by flutter_secure_storage (Keychain / Keystore).
class FlutterSecureStorageImpl implements SecureStorage {
  FlutterSecureStorageImpl({FlutterSecureStorage? storage})
    : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  @override
  Future<String?> read(String key) async => _storage.read(key: key);

  @override
  Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  @override
  Future<void> delete(String key) async => _storage.delete(key: key);
}

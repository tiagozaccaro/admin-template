/// Secure storage for OAuth tokens.
///
/// This is a placeholder in-memory implementation per T019. The concrete
/// production backing (flutter_secure_storage, iOS Keychain / Android
/// EncryptedSharedPreferences) is wired in T090+ when the Flutter auth
/// screen is implemented. No tokens are written to disk here.
abstract class SecureStorage {
  /// Read a value by key, or null when absent.
  Future<String?> read(String key);

  /// Write a value by key.
  Future<void> write(String key, String value);

  /// Delete a value by key.
  Future<void> delete(String key);
}

/// In-memory secure storage placeholder. Tokens live only in RAM and are
/// lost when the process restarts -- no long-lived on-device tokens
/// (constitution VI).
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

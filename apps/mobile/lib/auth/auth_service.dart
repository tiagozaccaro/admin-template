// Mobile authentication session.
//
// Coordinates the PKCE OAuth client and secure storage. The access token is
// persisted in platform secure storage (Keychain / Keystore) so the session
// survives process restarts.
import 'oauth_client.dart';
import 'secure_storage.dart';

class AuthService {
  AuthService(this._client, {SecureStorage? storage})
    : _storage = storage ?? InMemorySecureStorage();

  final OAuthClient _client;
  final SecureStorage _storage;

  static const _accessTokenKey = "admin_template_mobile_access_token";
  static const _refreshTokenKey = "admin_template_mobile_refresh_token";
  static const _expiresAtKey = "admin_template_mobile_expires_at";

  String? _accessToken;
  DateTime? _expiresAt;

  /// Whether a valid access token is currently held.
  bool get isAuthenticated =>
      _accessToken != null &&
      (_expiresAt == null || DateTime.now().isBefore(_expiresAt!));

  /// Current access token, or null when unauthenticated/expired.
  String? get accessToken => _accessToken;

  /// Current refresh token, or null.
  String? get refreshToken => _refreshToken;
  String? _refreshToken;

  /// Load any persisted session from secure storage.
  Future<void> loadSession() async {
    _accessToken = await _storage.read(_accessTokenKey);
    _refreshToken = await _storage.read(_refreshTokenKey);
    final expiresAt = await _storage.read(_expiresAtKey);
    _expiresAt = expiresAt == null ? null : DateTime.tryParse(expiresAt);
  }

  /// Persist the current session to secure storage.
  Future<void> _persist() async {
    if (_accessToken != null) {
      await _storage.write(_accessTokenKey, _accessToken!);
    }
    if (_refreshToken != null) {
      await _storage.write(_refreshTokenKey, _refreshToken!);
    }
    if (_expiresAt != null) {
      await _storage.write(_expiresAtKey, _expiresAt!.toIso8601String());
    }
  }

  /// Begin the authorization code flow; returns the provider URL to open.
  Future<Uri> login(String state) => _client.buildAuthorizationUrl(state);

  /// Complete the authorization code flow from the redirect and persist tokens.
  Future<void> handleCallback(String code, String state) async {
    final tokens = await _client.handleCallback(code, state);
    _accessToken = tokens.accessToken.isEmpty ? null : tokens.accessToken;
    _refreshToken = tokens.refreshToken;
    _expiresAt = tokens.expiresAt;
    await _persist();
  }

  /// Clear the session (logout) and remove persisted tokens.
  Future<void> logout() async {
    _accessToken = null;
    _refreshToken = null;
    _expiresAt = null;
    await _storage.delete(_accessTokenKey);
    await _storage.delete(_refreshTokenKey);
    await _storage.delete(_expiresAtKey);
    await _client.clearPkce();
  }
}

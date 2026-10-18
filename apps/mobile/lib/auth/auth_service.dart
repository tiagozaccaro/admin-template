// Mobile authentication session.
//
// Placeholder auth service. Coordinates the PKCE OAuth client
// and secure storage. Tokens live in memory only; no long-lived on-device
// tokens here.
import 'oauth_client.dart';

class AuthService {
  AuthService(this._client);

  final OAuthClient _client;

  String? _accessToken;
  DateTime? _expiresAt;

  /// Whether a valid access token is currently held in memory.
  bool get isAuthenticated =>
      _accessToken != null &&
      (_expiresAt == null || DateTime.now().isBefore(_expiresAt!));

  /// Current access token, or null when unauthenticated/expired.
  String? get accessToken => _accessToken;

  /// Begin the authorization code flow; returns the Keycloak URL to open.
  Future<Uri> login(String state) => _client.buildAuthorizationUrl(state);

  /// Complete the authorization code flow from the redirect.
  Future<void> handleCallback(String code, String state) async {
    final tokens = await _client.handleCallback(code, state);
    _accessToken = tokens.accessToken;
    _expiresAt = tokens.expiresAt;
  }

  /// Clear the in-memory session (logout).
  Future<void> logout() async {
    _accessToken = null;
    _expiresAt = null;
    await _client.clearPkce();
  }
}

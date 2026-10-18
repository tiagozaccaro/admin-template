/// Mobile authentication session.
///
/// Placeholder auth service per T019. Coordinates the PKCE OAuth client
/// and secure storage. Refresh-token persistence to secure storage is
/// wired in T090+ when the Flutter auth screen is implemented; here tokens
/// live in memory only (constitution VI).
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

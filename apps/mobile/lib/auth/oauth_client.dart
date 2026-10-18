/// OAuth 2.0 Authorization Code + PKCE client placeholder.
///
/// Placeholder for the mobile OIDC client per T019. Talks to the Keycloak
/// realm `contentforge` (client `contentforge-mobile`, PKCE, custom scheme
/// redirects). The actual HTTP token exchange and secure-storage wiring are
/// completed in T090+ when the Flutter auth screen is implemented.
///
/// No app-issued long-lived tokens are persisted to disk here
/// (constitution VI / AGENTS.md security).
import 'dart:convert';
import 'dart:math';

import 'secure_storage.dart';

class OAuthClient {
  OAuthClient({
    required this.issuer,
    required this.clientId,
    required this.redirectUri,
    this.scope = "openid profile email",
    SecureStorage? storage,
  }) : _storage = storage ?? InMemorySecureStorage();

  /// Keycloak issuer URL, e.g.
  /// `https://auth.contentforge.local/realms/contentforge`
  final String issuer;
  final String clientId;
  final String redirectUri;
  final String scope;
  final SecureStorage _storage;

  String get authorizationEndpoint => "$issuer/protocol/openid-connect/auth";
  String get tokenEndpoint => "$issuer/protocol/openid-connect/token";

  static const _verifierKey = "contentforge_mobile_pkce_verifier";
  static const _stateKey = "contentforge_mobile_pkce_state";

  /// Cryptographically random PKCE code verifier (43-128 chars).
  String generateCodeVerifier() {
    final values = List<int>.generate(32, (_) => nextInt(256));
    return base64Url.encode(values).replaceAll(RegExp(r"=+$"), "");
  }

  int nextInt(int bound) => _random.nextInt(bound);
  final _random = Random.secure();

  /// SHA-256 of the verifier, base64url-encoded (no padding).
  ///
  /// Placeholder: the real SHA-256 challenge is wired in T090+ when
  /// flutter_secure_storage and the HTTP token exchange are implemented.
  Future<String> codeChallenge(String verifier) async {
    return base64Url.encode(utf8.encode(verifier)).replaceAll(RegExp(r"=+$"), "");
  }

  /// Build the Keycloak authorization URL with PKCE and store verifier/state.
  Future<Uri> buildAuthorizationUrl(String state) async {
    final verifier = generateCodeVerifier();
    await _storage.write(_verifierKey, verifier);
    await _storage.write(_stateKey, state);
    final challenge = await codeChallenge(verifier);
    return Uri.parse(authorizationEndpoint).replace(queryParameters: <String, String>{
      "client_id": clientId,
      "response_type": "code",
      "scope": scope,
      "redirect_uri": redirectUri,
      "code_challenge": challenge,
      "code_challenge_method": "S256",
      "state": state,
    });
  }

  /// Exchange the authorization code for tokens.
  ///
  /// Placeholder: validates PKCE state/verifier and returns a [TokenSet]
  /// without performing the real HTTP exchange (wired in T090+).
  Future<TokenSet> handleCallback(String code, String state) async {
    final expectedState = await _storage.read(_stateKey);
    if (expectedState == null || expectedState != state) {
      throw const FormatException("OIDC state mismatch");
    }
    final verifier = await _storage.read(_verifierKey);
    if (verifier == null) {
      throw const FormatException("OIDC code verifier missing");
    }
    await _storage.delete(_verifierKey);
    await _storage.delete(_stateKey);

    return TokenSet(
      accessToken: "placeholder-access-token",
      idToken: null,
      refreshToken: null,
      expiresAt: null,
    );
  }

  /// Clear stored PKCE verifier/state (logout).
  Future<void> clearPkce() async {
    await _storage.delete(_verifierKey);
    await _storage.delete(_stateKey);
  }
}

/// Tokens held by the OAuth client.
class TokenSet {
  const TokenSet({
    required this.accessToken,
    this.idToken,
    this.refreshToken,
    this.expiresAt,
  });

  final String accessToken;
  final String? idToken;
  final String? refreshToken;
  final DateTime? expiresAt;
}

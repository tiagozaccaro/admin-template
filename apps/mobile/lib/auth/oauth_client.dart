// OAuth 2.0 Authorization Code + PKCE client.
//
// Talks to the OIDC provider (Google) token endpoint to exchange the
// authorization code for tokens. PKCE code challenge uses SHA-256 and tokens
// are returned to the caller for persistence in secure storage.
// No app-issued long-lived tokens are persisted to disk here.
import 'dart:convert';
import 'dart:math';

import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;

import 'secure_storage.dart';

class OAuthClient {
  OAuthClient({
    required this.issuer,
    required this.clientId,
    required this.redirectUri,
    this.scope = "openid profile email",
    SecureStorage? storage,
    http.Client? httpClient,
  }) : _storage = storage ?? InMemorySecureStorage(),
       _httpClient = httpClient ?? http.Client();

  /// OIDC issuer URL, e.g.
  /// `https://accounts.google.com`
  final String issuer;
  final String clientId;
  final String redirectUri;
  final String scope;
  final SecureStorage _storage;
  final http.Client _httpClient;

  String get authorizationEndpoint => "$issuer/oauth2/v2/auth";
  String get tokenEndpoint => "$issuer/oauth2/v2/token";

  static const _verifierKey = "admin_template_mobile_pkce_verifier";
  static const _stateKey = "admin_template_mobile_pkce_state";

  /// Cryptographically random PKCE code verifier (43-128 chars).
  String generateCodeVerifier() {
    final values = List<int>.generate(32, (_) => _secureRandom.nextInt(256));
    return base64Url.encode(values).replaceAll(RegExp(r"=+$"), "");
  }

  final _secureRandom = Random.secure();

  /// SHA-256 of the verifier, base64url-encoded (no padding).
  String codeChallenge(String verifier) {
    final digest = sha256.convert(utf8.encode(verifier));
    return base64Url.encode(digest.bytes).replaceAll(RegExp(r"=+$"), "");
  }

  /// Build the provider authorization URL with PKCE and store verifier/state.
  Future<Uri> buildAuthorizationUrl(String state) async {
    final verifier = generateCodeVerifier();
    await _storage.write(_verifierKey, verifier);
    await _storage.write(_stateKey, state);
    final challenge = codeChallenge(verifier);
    return Uri.parse(authorizationEndpoint).replace(
      queryParameters: <String, String>{
        "client_id": clientId,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirectUri,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
      },
    );
  }

  /// Exchange the authorization code for tokens via the token endpoint.
  ///
  /// Validates PKCE state/verifier, performs the real HTTP token exchange,
  /// and returns a [TokenSet] with the provider-issued tokens.
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

    final response = await _httpClient.post(
      Uri.parse(tokenEndpoint),
      headers: <String, String>{
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
      },
      body: <String, String>{
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirectUri,
        "client_id": clientId,
        "code_verifier": verifier,
      },
    );

    if (response.statusCode >= 400) {
      throw FormatException(
        "Token exchange failed: ${response.statusCode} ${response.body}",
      );
    }

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    final expiresIn = body["expires_in"] is num
        ? (body["expires_in"] as num).toInt()
        : null;
    final expiresAt = expiresIn == null
        ? null
        : DateTime.now().add(Duration(seconds: expiresIn));

    return TokenSet(
      accessToken: body["access_token"] as String? ?? "",
      idToken: body["id_token"] as String?,
      refreshToken: body["refresh_token"] as String?,
      expiresAt: expiresAt,
    );
  }

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

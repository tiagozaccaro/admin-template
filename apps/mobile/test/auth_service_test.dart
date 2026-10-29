import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/auth/auth_service.dart';
import 'package:mobile/auth/oauth_client.dart';
import 'package:mobile/auth/secure_storage.dart';

void main() {
  test('AuthService starts unauthenticated', () {
    final storage = InMemorySecureStorage();
    final client = OAuthClient(
      issuer: 'http://localhost:8080/realms/admin-template',
      clientId: 'admin-template-mobile',
      redirectUri: 'admin-template://auth/callback',
      storage: storage,
    );
    final service = AuthService(client, storage: storage);
    expect(service.isAuthenticated, isFalse);
    expect(service.accessToken, isNull);
  });

  test('loadSession restores persisted tokens', () async {
    final storage = InMemorySecureStorage();
    await storage.write('admin_template_mobile_access_token', 'abc');
    await storage.write('admin_template_mobile_refresh_token', 'ref');
    final future = DateTime.now().add(const Duration(hours: 1));
    await storage.write('admin_template_mobile_expires_at', future.toIso8601String());

    final client = OAuthClient(
      issuer: 'http://localhost:8080/realms/admin-template',
      clientId: 'c',
      redirectUri: 'r',
      storage: storage,
    );
    final service = AuthService(client, storage: storage);
    await service.loadSession();
    expect(service.isAuthenticated, isTrue);
    expect(service.accessToken, 'abc');
    expect(service.refreshToken, 'ref');
  });

  test('handleCallback persists tokens', () async {
    final storage = InMemorySecureStorage();
    final mockClient = MockClient((request) async {
      return http.Response(
        jsonEncode({
          'access_token': 'access-123',
          'refresh_token': 'refresh-456',
          'expires_in': 3600,
        }),
        200,
        headers: {'content-type': 'application/json'},
      );
    });
    final oauth = OAuthClient(
      issuer: 'http://localhost:8080/realms/admin-template',
      clientId: 'c',
      redirectUri: 'r',
      storage: storage,
      httpClient: mockClient,
    );
    final service = AuthService(oauth, storage: storage);
    // prime pkce state
    await oauth.buildAuthorizationUrl('state-1');
    await service.handleCallback('code-1', 'state-1');
    expect(service.isAuthenticated, isTrue);
    expect(service.accessToken, 'access-123');
    expect(await storage.read('admin_template_mobile_access_token'), 'access-123');
  });

  test('logout clears session', () async {
    final storage = InMemorySecureStorage();
    final oauth = OAuthClient(
      issuer: 'http://localhost:8080/realms/admin-template',
      clientId: 'c',
      redirectUri: 'r',
      storage: storage,
    );
    final service = AuthService(oauth, storage: storage);
    await storage.write('admin_template_mobile_access_token', 'abc');
    await service.loadSession();
    await service.logout();
    expect(service.isAuthenticated, isFalse);
    expect(service.accessToken, isNull);
    expect(await storage.read('admin_template_mobile_access_token'), isNull);
  });
}
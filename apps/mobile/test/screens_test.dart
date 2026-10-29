import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/auth/auth_service.dart';
import 'package:mobile/auth/oauth_client.dart';
import 'package:mobile/auth/secure_storage.dart';
import 'package:mobile/features/auth/auth_gate.dart';
import 'package:mobile/features/auth/login_screen.dart';

void main() {
  testWidgets('AuthGate shows login screen when unauthenticated', (tester) async {
    final storage = InMemorySecureStorage();
    final oauthClient = OAuthClient(
      issuer: 'http://localhost:8080/realms/admin-template',
      clientId: 'admin-template-mobile',
      redirectUri: 'admin-template://auth/callback',
      storage: storage,
    );
    final authService = AuthService(oauthClient, storage: storage);

    await tester.pumpWidget(MaterialApp(home: AuthGate(authService: authService)));
    await tester.pump();

    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Signed in — admin dashboard'), findsNothing);
  });

  testWidgets('LoginScreen renders sign in button', (tester) async {
    final storage = InMemorySecureStorage();
    final oauthClient = OAuthClient(
      issuer: 'http://localhost:8080/realms/admin-template',
      clientId: 'admin-template-mobile',
      redirectUri: 'admin-template://auth/callback',
      storage: storage,
    );
    final authService = AuthService(oauthClient, storage: storage);

    await tester.pumpWidget(MaterialApp(home: LoginScreen(authService: authService)));
    await tester.pump();

    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Sign in to your workspace'), findsOneWidget);
  });
}
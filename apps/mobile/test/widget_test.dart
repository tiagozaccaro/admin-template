// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/auth/auth_service.dart';
import 'package:mobile/auth/oauth_client.dart';
import 'package:mobile/auth/secure_storage.dart';
import 'package:mobile/features/auth/auth_gate.dart';

void main() {
  testWidgets('AuthGate shows login screen when unauthenticated', (
    WidgetTester tester,
  ) async {
    final storage = InMemorySecureStorage();
    final oauthClient = OAuthClient(
      issuer: "http://localhost:8080/realms/admin-template",
      clientId: "admin-template-mobile",
      redirectUri: "admin-template://auth/callback",
      storage: storage,
    );
    final authService = AuthService(oauthClient);

    await tester.pumpWidget(MaterialApp(
      home: AuthGate(authService: authService),
    ));

    expect(find.text("Sign in with Keycloak"), findsOneWidget);
    expect(find.text("Signed in"), findsNothing);
  });
}

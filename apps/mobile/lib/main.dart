import 'package:flutter/material.dart';
import 'package:mobile/auth/auth_service.dart';
import 'package:mobile/auth/oauth_client.dart';
import 'package:mobile/auth/secure_storage.dart';
import 'package:mobile/features/auth/auth_gate.dart';

void main() {
  runApp(const ContentForgeApp());
}

class ContentForgeApp extends StatelessWidget {
  const ContentForgeApp({super.key});

  @override
  Widget build(BuildContext context) {
    final storage = InMemorySecureStorage();
    final oauthClient = OAuthClient(
      issuer: const String.fromEnvironment(
        "CONTENT_FORGE_OIDC_ISSUER",
        defaultValue: "http://localhost:8080/realms/contentforge",
      ),
      clientId: const String.fromEnvironment(
        "CONTENT_FORGE_OIDC_CLIENT_ID",
        defaultValue: "contentforge-mobile",
      ),
      redirectUri: const String.fromEnvironment(
        "CONTENT_FORGE_OIDC_REDIRECT_URI",
        defaultValue: "contentforge://auth/callback",
      ),
      storage: storage,
    );
    final authService = AuthService(oauthClient);

    return MaterialApp(
      title: "Admin Template",
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: AuthGate(authService: authService),
    );
  }
}

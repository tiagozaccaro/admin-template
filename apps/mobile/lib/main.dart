import 'package:flutter/material.dart';
import 'package:mobile/auth/auth_service.dart';
import 'package:mobile/auth/oauth_client.dart';
import 'package:mobile/auth/secure_storage.dart';
import 'package:mobile/features/auth/auth_gate.dart';

void main() {
  runApp(const AdminTemplateApp());
}

class AdminTemplateApp extends StatelessWidget {
  const AdminTemplateApp({super.key});

  @override
  Widget build(BuildContext context) {
    final storage = FlutterSecureStorageImpl();
    final oauthClient = OAuthClient(
      issuer: const String.fromEnvironment(
        "ADMIN_TEMPLATE_OIDC_ISSUER",
        defaultValue: "https://accounts.google.com",
      ),
      clientId: const String.fromEnvironment(
        "ADMIN_TEMPLATE_OIDC_CLIENT_ID",
        defaultValue: "admin-template-mobile",
      ),
      redirectUri: const String.fromEnvironment(
        "ADMIN_TEMPLATE_OIDC_REDIRECT_URI",
        defaultValue: "admin-template://auth/callback",
      ),
      storage: storage,
    );
    final authService = AuthService(oauthClient, storage: storage);

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

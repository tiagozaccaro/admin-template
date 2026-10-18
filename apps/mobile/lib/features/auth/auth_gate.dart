/// Flutter authentication gate.
///
/// Routes to the login screen when unauthenticated, otherwise to the
/// content home screen. Per contracts/auth-oidc.md: Authorization Code +
/// PKCE via Keycloak, no app-issued long-lived tokens.

import 'package:flutter/material.dart';
import 'package:mobile/auth/auth_service.dart';
import 'login_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key, required this.authService});

  final AuthService authService;

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    // AuthService holds tokens in memory; on cold start we are
    // unauthenticated until the user completes the PKCE flow.
    if (!mounted) return;
    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    if (widget.authService.isAuthenticated) {
      return const ContentPlaceholder();
    }
    return LoginScreen(authService: widget.authService);
  }
}

/// Placeholder content home shown after successful login.
class ContentPlaceholder extends StatelessWidget {
  const ContentPlaceholder({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Admin Template")),
      body: const Center(child: Text("Signed in — admin dashboard in T092")),
    );
  }
}

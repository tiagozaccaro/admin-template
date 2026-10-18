/// Flutter login screen.
///
/// Initiates the OIDC Authorization Code + PKCE flow via Keycloak and
/// handles the redirect callback. Per contracts/auth-oidc.md: no
/// app-issued long-lived tokens are persisted (constitution VI).

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:mobile/auth/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.authService});

  final AuthService authService;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _loggingIn = false;
  String? _error;

  Future<void> _handleLogin() async {
    setState(() {
      _loggingIn = true;
      _error = null;
    });
    try {
      // Generate a random state to bind this request to the callback.
      final state = _randomState();
      final url = await widget.authService.login(state);

      // On mobile, launch the system browser for the authorization URL.
      // The callback is handled via the registered redirect URI custom
      // scheme (e.g. admin-template://auth/callback). On web, this would
      // be http://localhost:3000/auth/callback handled by the Next.js
      // route at apps/web/src/app/auth/callback/route.tsx.
      // TODO: wire platform-specific URL launcher + callback listener
      // in T090+; here we navigate to the callback page so the code/state
      // can be exchanged in-process (development simplification).
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => CallbackScreen(
            authService: widget.authService,
            authorizationUrl: url,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loggingIn = false);
    }
  }

  String _randomState() {
    final values = List<int>.generate(16, (_) => 48 + (DateTime.now().millisecond % 75));
    return String.fromCharCodes(values);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Sign in to Admin Template")),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "Sign in to your workspace",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 32),
              if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  color: Colors.red.shade50,
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),
              ],
                FilledButton(
                  onPressed: _loggingIn ? null : _handleLogin,
                  child: _loggingIn
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text("Sign in"),
                ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: _loggingIn ? null : () => setState(() => _error = null),
                child: const Text("Cancel"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// In-process PKCE callback screen (development simplification).
///
/// Receives the authorization URL, exchanges the code/state for tokens,
/// and stores them in AuthService (memory only). On production mobile,
/// this is replaced by a custom-scheme redirect listener.
class CallbackScreen extends StatefulWidget {
  const CallbackScreen({
    super.key,
    required this.authService,
    required this.authorizationUrl,
  });

  final AuthService authService;
  final Uri authorizationUrl;

  @override
  State<CallbackScreen> createState() => _CallbackScreenState();
}

class _CallbackScreenState extends State<CallbackScreen> {
  bool _exchanging = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _exchange();
  }

  Future<void> _exchange() async {
    // Extract code/state from the authorization URL's redirect target.
    // In a real mobile build, the OS delivers the redirect URI to this
    // screen; here we simulate by parsing a ?code=&state= query appended
    // to the same page via query parameters.
    final code = _queryParam(widget.authorizationUrl, "code");
    final state = _queryParam(widget.authorizationUrl, "state");
    if (code == null || state == null) {
      // No code yet: show the authorization URL as a deep-link target.
      if (!mounted) return;
      setState(() => _error = "Open the authorization URL and complete sign-in");
      return;
    }
    setState(() => _exchanging = true);
    try {
      await widget.authService.handleCallback(code, state);
      if (!mounted) return;
      Navigator.pushReplacementNamed(context, "/");
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _exchanging = false);
    }
  }

  String? _queryParam(Uri url, String name) => url.queryParameters[name];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Completing sign-in")),
      body: Center(
        child: _exchanging
            ? const CircularProgressIndicator()
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(_error ?? "Authorization pending"),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text("Back"),
                  ),
                ],
              ),
      ),
    );
  }
}

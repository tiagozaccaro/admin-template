import "package:flutter/material.dart";
import "package:http/http.dart" as http;
import "dart:convert";

import "agent_chat_screen.dart";

class AgentListScreen extends StatefulWidget {
  const AgentListScreen({super.key});

  @override
  State<AgentListScreen> createState() => _AgentListScreenState();
}

class _AgentListScreenState extends State<AgentListScreen> {
  static const _apiBase = String.fromEnvironment(
    "API_BASE_URL",
    defaultValue: "http://localhost:8000",
  );

  bool _loading = true;
  String? _error;
  List<_Agent> _agents = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final client = http.Client();
      try {
        final resp = await client.get(
          Uri.parse("$_apiBase/api/v1/agents"),
        );
        if (resp.statusCode != 200) {
          throw Exception("HTTP ${resp.statusCode}");
        }
        final body = jsonDecode(resp.body) as List;
        final agents = body
            .map((e) => _Agent(
                  id: e["id"] as String,
                  name: e["name"] as String,
                  url: e["url"] as String,
                  token: e["token"] as String?,
                  status: e["status"] as String? ?? "offline",
                ))
            .toList();
        if (!mounted) return;
        setState(() {
          _agents = agents;
          _loading = false;
        });
      } finally {
        client.close();
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Color _statusColor(String status, BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    switch (status) {
      case "healthy":
        return Colors.green;
      case "unhealthy":
        return Colors.amber;
      case "offline":
        return isDark ? Colors.grey[400]! : Colors.grey;
      default:
        return Colors.blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    if (_error != null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48),
                const SizedBox(height: 12),
                const Text("Failed to load agents"),
                const SizedBox(height: 8),
                Text(
                  _error!,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: _load,
                  child: const Text("Retry"),
                ),
              ],
            ),
          ),
        ),
      );
    }
    if (_agents.isEmpty) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.computer, size: 56),
                const SizedBox(height: 12),
                const Text("No agents registered"),
                const SizedBox(height: 4),
                Text(
                  "Register a standalone agent to begin chatting.",
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      );
    }
    return Scaffold(
      appBar: AppBar(title: const Text("Agents")),
      body: ListView.builder(
        itemCount: _agents.length,
        itemBuilder: (context, index) {
          final agent = _agents[index];
          final color = _statusColor(agent.status, context);
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: color.withValues(alpha: 0.15),
                child: Icon(Icons.computer, color: color),
              ),
              title: Text(agent.name),
              subtitle: Text(agent.url),
              trailing: Chip(
                label: Text(agent.status),
                labelStyle: TextStyle(color: color),
              ),
              onTap: () {
                Navigator.push(
                  context,
                  PageRouteBuilder(
                    pageBuilder: (context, animation, secondaryAnimation) =>
                        AgentChatScreen(
                      agentId: agent.id,
                      agentName: agent.name,
                      agentUrl: agent.url,
                      token: agent.token,
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _Agent {
  const _Agent({
    required this.id,
    required this.name,
    required this.url,
    this.token,
    required this.status,
  });

  final String id;
  final String name;
  final String url;
  final String? token;
  final String status;
}
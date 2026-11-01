import "dart:convert";
import "package:flutter/material.dart";
import "package:http/http.dart" as http;

class AgentChatScreen extends StatefulWidget {
  const AgentChatScreen({
    super.key,
    required this.agentId,
    required this.agentName,
    this.agentUrl,
    this.token,
  });

  final String agentId;
  final String agentName;
  final String? agentUrl;
  final String? token;

  @override
  State<AgentChatScreen> createState() => _AgentChatScreenState();
}

class _AgentChatScreenState extends State<AgentChatScreen> {
  static const _fallbackApiBase = String.fromEnvironment(
    "API_BASE_URL",
    defaultValue: "http://localhost:8000",
  );

  final List<_ChatMessage> _messages = [];
  final _inputController = TextEditingController();
  bool _sending = false;
  String? _sessionId;

  String get _endpoint {
    final base = (widget.agentUrl ?? _fallbackApiBase).replaceFirst(
      RegExp(r"/+$"),
      "",
    );
    return "$base/chat/agent";
  }

  Future<void> _send(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || _sending) return;

    _sessionId ??= "mobile-${DateTime.now().millisecondsSinceEpoch}";
    setState(() {
      _messages.add(_ChatMessage(role: "user", content: trimmed));
      _sending = true;
    });
    _inputController.clear();

    final assistantMsg = _ChatMessage(role: "assistant", content: "");
    if (!mounted) return;
    setState(() => _messages.add(assistantMsg));

    final client = http.Client();
    try {
      final request = http.Request("POST", Uri.parse(_endpoint));
      request.headers["Content-Type"] = "application/json";
      if (widget.token != null && widget.token!.isNotEmpty) {
        request.headers["Authorization"] = "Bearer ${widget.token}";
      }
      request.body = jsonEncode({
        "prompt_input": trimmed,
        "model": "test",
        "session_id": _sessionId,
      });

      final response = await client.send(request);
      final stream = response.stream
          .transform(utf8.decoder)
          .transform(const LineSplitter());

      await for (final line in stream) {
        if (!line.startsWith("data: ")) continue;
        final data = line.substring(6).trim();
        if (data == "[DONE]") break;
        Map<String, dynamic>? parsed;
        try {
          parsed = jsonDecode(data) as Map<String, dynamic>?;
        } catch (_) {
          // Treat as raw text delta.
          if (!mounted) continue;
          setState(() {
            final idx = _messages.indexWhere(
              (m) => m.id == assistantMsg.id,
            );
            if (idx >= 0) {
              _messages[idx] = _ChatMessage(
                role: "assistant",
                content: _messages[idx].content + data,
              );
            }
          });
          continue;
        }
        if (parsed?["error"] != null) {
          if (!mounted) continue;
          setState(() {
            final idx = _messages.indexWhere((m) => m.id == assistantMsg.id);
            if (idx >= 0) {
              _messages[idx] = _ChatMessage(
                role: "assistant",
                content: "Error: ${parsed?["error"]}",
              );
            }
          });
          break;
        }
        final approval = parsed?["approval_request"];
        if (approval is Map<String, dynamic> && mounted) {
          final approvalUrl = approval["url"] as String?;
          if (approvalUrl != null && approvalUrl.isNotEmpty) {
            setState(() {
              final idx = _messages.indexWhere((m) => m.id == assistantMsg.id);
              if (idx >= 0) {
                _messages[idx] = _ChatMessage(
                  role: "assistant",
                  content:
                      "Approval required: ${approval["summary"] ?? approval["tool_name"]}. "
                      "Resolve on the web UI.",
                );
              }
            });
            continue;
          }
          final approvalId = approval["id"] as String?;
          if (approvalId != null) {
            _showApprovalDialog(approvalId, approval);
          }
          continue;
        }
        final delta = parsed?["delta"] as String?;
        if (delta != null && delta.isNotEmpty && mounted) {
          setState(() {
            final idx = _messages.indexWhere((m) => m.id == assistantMsg.id);
            if (idx >= 0) {
              _messages[idx] = _ChatMessage(
                role: "assistant",
                content: _messages[idx].content + delta,
              );
            }
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          final idx = _messages.indexWhere((m) => m.id == assistantMsg.id);
          if (idx >= 0) {
            _messages[idx] = _ChatMessage(
              role: "assistant",
              content: "Request failed: $e",
            );
          }
        });
      }
    } finally {
      client.close();
      if (mounted) {
        setState(() => _sending = false);
      }
    }
  }

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  Future<void> _approve(String approvalId, bool approved) async {
    final endpoint = _endpoint.replaceFirst(RegExp(r"/chat/agent$"), "/approve/$approvalId");
    try {
      final request = http.Request("POST", Uri.parse(endpoint));
      request.headers["Content-Type"] = "application/json";
      if (widget.token != null && widget.token!.isNotEmpty) {
        request.headers["Authorization"] = "Bearer ${widget.token}";
      }
      request.body = jsonEncode({"approved": approved});
      final response = await http.Client().send(request);
      await response.stream.drain<void>();
    } catch (_) {
      // Best-effort: the SSE stream will surface the error.
    }
  }

  void _showApprovalDialog(
    String approvalId,
    Map<String, dynamic> approval,
  ) {
    if (!mounted) return;
    final toolName = approval["tool_name"] as String? ?? "unknown";
    final summary = approval["summary"] as String? ?? "";
    final args = approval["args"] as Map<String, dynamic>? ?? {};
    final argsText = args.entries
        .map((e) => "${e.key}: ${e.value}")
        .join(", ");
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text("Approval required"),
        content: Text(
          "The agent wants to run $toolName.\n\n"
          "Args: $argsText\n\n"
          "$summary",
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              _approve(approvalId, false);
            },
            child: const Text("Deny"),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              _approve(approvalId, true);
            },
            child: const Text("Approve"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.agentName)),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message.role == "user";
                return Align(
                  alignment: isUser
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: isUser
                          ? Theme.of(context).colorScheme.primaryContainer
                          : Theme.of(
                              context,
                            ).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(message.content),
                  ),
                );
              },
            ),
          ),
          const Divider(height: 1),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _inputController,
                    textInputAction: TextInputAction.send,
                    onSubmitted: _send,
                    enabled: !_sending,
                  ),
                ),
                IconButton(
                  onPressed: _sending
                      ? null
                      : () => _send(_inputController.text),
                  icon: _sending
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatMessage {
  _ChatMessage({String? id, required this.role, required this.content})
    : id = id ?? UniqueKey().toString();

  final String id;
  final String role;
  final String content;
}
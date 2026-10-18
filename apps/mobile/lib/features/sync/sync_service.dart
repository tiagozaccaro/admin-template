/// Sync service: push/pull between local drift DB and the API
/// (T091). Implements GET /sync/changes (pull) and POST /sync/push
/// (push) per contracts/sync-api.md.

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/features/sync/sync_database.dart';

class SyncService {
  SyncService({required this.baseUrl, required this.userId, required this.db});

  final String baseUrl;
  final String userId;
  final SyncDatabase db;

  /// Pull changes from the server since `cursor`, apply them locally.
  Future<List<SyncChange>> pull({String? cursor, int limit = 50}) async {
    final uri = Uri.parse("$baseUrl/api/v1/sync/changes").replace(
      queryParameters: {
        "user_id": userId,
        if (cursor != null) "cursor": cursor,
        "limit": limit.toString(),
      },
    );
    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw SyncException("Pull failed: ${response.statusCode}");
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final items = (data["items"] as List? ?? []);
    for (final item in items) {
      await _applyChange(item as Map<String, dynamic>);
    }
    return [
      for (final item in items) SyncChange.fromMap(item),
    ];
  }

  /// Push local changes to the server. Returns per-op results.
  Future<List<SyncPushResult>> push(
    List<SyncPushOp> ops, {
    String? idempotencyKey,
  }) async {
    final body = jsonEncode({
      "ops": [
        for (final op in ops)
          {
            "op_id": op.opId,
            "entity_type": op.entityType,
            "entity_id": op.entityId,
            "base_revision": op.baseRevision,
            "patch": op.patch,
          }
      ],
    });
    final headers = <String, String>{
      "Content-Type": "application/json",
      if (idempotencyKey != null) "Idempotency-Key": idempotencyKey,
    };
    final response = await http.post(
      Uri.parse("$baseUrl/api/v1/sync/push"),
      headers: headers,
      body: body,
    );
    if (response.statusCode != 200) {
      throw SyncException("Push failed: ${response.statusCode}");
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final results = (data["results"] as List? ?? []);
    return [
      for (final result in results) SyncPushResult.fromMap(result),
    ];
  }

  Future<void> _applyChange(Map<String, dynamic> item) async {
    final entityType = item["entity_type"] as String;
    final entityId = item["entity_id"] as String;
    final revision = item["revision"] as int;
    final payload = item["payload"] as Map<String, dynamic>;
    final authorId = item["author"] as String;
    final createdAt = DateTime.parse(item["created_at"] as String);
    final priorRevisionId = item["prior_revision_id"] as String?;

    await db.insertRevision(SyncContentRevision(
      id: item["id"]?.toString() ?? _newId(),
      entityType: entityType,
      entityId: entityId,
      revision: revision,
      authorId: authorId,
      createdAt: createdAt,
      payload: payload,
      priorRevisionId: priorRevisionId,
      idempotencyKey: item["idempotency_key"] as String?,
    ));
    // Upsert the draft/content_item head if it's a draft.
    if (entityType == "content_item") {
      await db.upsertDraft(SyncDraft(
        id: entityId,
        contentItemId: entityId,
        currentRevisionId: item["id"]?.toString(),
        updatedAt: createdAt,
      ));
    }
  }

  String _newId() {
    final now = DateTime.now().millisecondsSinceEpoch;
    return "mobile-$now";
  }
}

/// A change returned from /sync/changes.
class SyncChange {
  SyncChange({
    required this.entityType,
    required this.entityId,
    required this.revision,
    required this.payload,
    required this.author,
    required this.createdAt,
  });

  factory SyncChange.fromMap(Map<String, dynamic> m) => SyncChange(
        entityType: m["entity_type"] as String,
        entityId: m["entity_id"] as String,
        revision: m["revision"] as int,
        payload: Map<String, dynamic>.from(m["payload"] as Map),
        author: m["author"] as String,
        createdAt: DateTime.parse(m["created_at"] as String),
      );

  final String entityType;
  final String entityId;
  final int revision;
  final Map<String, dynamic> payload;
  final String author;
  final DateTime createdAt;
}

/// A push operation to send to /sync/push.
class SyncPushOp {
  SyncPushOp({
    required this.opId,
    required this.entityType,
    required this.entityId,
    required this.baseRevision,
    required this.patch,
  });

  final String opId;
  final String entityType;
  final String entityId;
  final int baseRevision;
  final Map<String, dynamic> patch;
}

/// Result of a single push op.
class SyncPushResult {
  SyncPushResult({
    required this.opId,
    required this.status,
    this.serverRevision,
    this.conflictRevisionId,
  });

  factory SyncPushResult.fromMap(Map<String, dynamic> m) => SyncPushResult(
        opId: m["op_id"] as String,
        status: m["status"] as String,
        serverRevision: m["server_revision"] as int?,
        conflictRevisionId: m["conflict_revision_id"] as String?,
      );

  final String opId;
  final String status;
  final int? serverRevision;
  final String? conflictRevisionId;
}

class SyncException implements Exception {
  SyncException(this.message);
  final String message;
  @override
  String toString() => message;
}

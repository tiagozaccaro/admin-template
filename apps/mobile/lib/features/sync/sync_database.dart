/// Local SQLite database for offline-first sync (T091).
///
/// Mirrors the server's project/draft/revision tables so the mobile app
/// can read and write offline, then sync with the API via
/// GET /sync/changes and POST /sync/push (contracts/sync-api.md).

import 'dart:convert';
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

part 'sync_database.g.dart';

const _kDbName = "admin_template.db";

class Projects extends Table {
  TextColumn get id => text()();
  TextColumn get workspaceId => text()();
  TextColumn get name => text()();
  TextColumn get createdBy => text()();
  DateTimeColumn get createdAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class ContentItems extends Table {
  TextColumn get id => text()();
  TextColumn get workspaceId => text()();
  TextColumn get projectId => text().nullable()();
  TextColumn get kind => text()();
  TextColumn get authorId => text()();
  DateTimeColumn get createdAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class Drafts extends Table {
  TextColumn get id => text()();
  TextColumn get contentItemId => text()();
  TextColumn get currentRevisionId => text().nullable()();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class ContentRevisions extends Table {
  TextColumn get id => text()();
  TextColumn get entityType => text()();
  TextColumn get entityId => text()();
  IntColumn get revision => integer()();
  TextColumn get authorId => text()();
  DateTimeColumn get createdAt => dateTime()();
  TextColumn get payload => text()(); // JSON
  TextColumn get priorRevisionId => text().nullable()();
  TextColumn get idempotencyKey => text().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, _kDbName));
    return NativeDatabase(file);
  });
}

@DriftDatabase(tables: [Projects, ContentItems, Drafts, ContentRevisions])
class SyncDatabase extends _$SyncDatabase {
  SyncDatabase() : super(_openConnection());

  /// Create a SyncDatabase backed by an existing [QueryExecutor] (testing).
  SyncDatabase.forTesting(QueryExecutor e) : super(e);

  @override
  int get schemaVersion => 1;

  /// Insert or update a project (upsert by id).
  Future<void> upsertProject(SyncProject project) {
    return into(projects).insertOnConflictUpdate(project.toCompanion());
  }

  /// Insert or update a draft (upsert by id).
  Future<void> upsertDraft(SyncDraft draft) {
    return into(drafts).insertOnConflictUpdate(draft.toCompanion());
  }

  /// Insert a content revision (append-only).
  Future<void> insertRevision(SyncContentRevision revision) {
    return into(contentRevisions).insert(revision.toCompanion());
  }

  /// Get all projects.
  Future<List<SyncProject>> getAllProjects() async {
    final rows = await select(projects).get();
    return rows
        .map((row) => SyncProject(
              id: row.id,
              workspaceId: row.workspaceId,
              name: row.name,
              createdBy: row.createdBy,
              createdAt: row.createdAt,
            ))
        .toList();
  }

  /// Get all drafts.
  Future<List<SyncDraft>> getAllDrafts() async {
    final rows = await select(drafts).get();
    return rows
        .map((row) => SyncDraft(
              id: row.id,
              contentItemId: row.contentItemId,
              currentRevisionId: row.currentRevisionId,
              updatedAt: row.updatedAt,
            ))
        .toList();
  }

  /// Get revisions for an entity, ordered by revision ascending.
  Future<List<SyncContentRevision>> getRevisionsForEntity(
    String entityId, [
    String entityType = "content_item",
  ]) async {
    final rows = await (select(contentRevisions)
          ..where((r) =>
              r.entityId.equals(entityId) & r.entityType.equals(entityType)))
        .get();
    rows.sort((a, b) => a.revision.compareTo(b.revision));
    return rows
        .map((row) => SyncContentRevision(
              id: row.id,
              entityType: row.entityType,
              entityId: row.entityId,
              revision: row.revision,
              authorId: row.authorId,
              createdAt: row.createdAt,
              payload: _jsonDecode(row.payload),
              priorRevisionId: row.priorRevisionId,
              idempotencyKey: row.idempotencyKey,
            ))
        .toList();
  }

  /// Clear all local data (for sync reset / logout).
  Future<void> clear() async {
    await (delete(contentRevisions)).go();
    await (delete(drafts)).go();
    await (delete(contentItems)).go();
    await (delete(projects)).go();
  }
}

/// Data classes mirroring the drift tables.
class SyncProject {
  final String id;
  final String workspaceId;
  final String name;
  final String createdBy;
  final DateTime createdAt;

  SyncProject({
    required this.id,
    required this.workspaceId,
    required this.name,
    required this.createdBy,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() => {
        "id": id,
        "workspace_id": workspaceId,
        "name": name,
        "created_by": createdBy,
        "created_at": createdAt.toIso8601String(),
      };
}

class SyncDraft {
  final String id;
  final String contentItemId;
  final String? currentRevisionId;
  final DateTime updatedAt;

  SyncDraft({
    required this.id,
    required this.contentItemId,
    this.currentRevisionId,
    required this.updatedAt,
  });
}

class SyncContentRevision {
  final String id;
  final String entityType;
  final String entityId;
  final int revision;
  final String authorId;
  final DateTime createdAt;
  final Map<String, dynamic> payload;
  final String? priorRevisionId;
  final String? idempotencyKey;

  SyncContentRevision({
    required this.id,
    required this.entityType,
    required this.entityId,
    required this.revision,
    required this.authorId,
    required this.createdAt,
    required this.payload,
    this.priorRevisionId,
    this.idempotencyKey,
  });
}

extension _ProjectCompanion on SyncProject {
  ProjectsCompanion toCompanion() => ProjectsCompanion.insert(
        id: id,
        workspaceId: workspaceId,
        name: name,
        createdBy: createdBy,
        createdAt: createdAt,
      );
}

extension _DraftCompanion on SyncDraft {
  DraftsCompanion toCompanion() => DraftsCompanion.insert(
        id: id,
        contentItemId: contentItemId,
        currentRevisionId: Value(currentRevisionId),
        updatedAt: updatedAt,
      );
}

extension _RevisionCompanion on SyncContentRevision {
  ContentRevisionsCompanion toCompanion() => ContentRevisionsCompanion.insert(
        id: id,
        entityType: entityType,
        entityId: entityId,
        revision: revision,
        authorId: authorId,
        createdAt: createdAt,
        payload: _jsonEncode(payload),
        priorRevisionId: Value(priorRevisionId),
        idempotencyKey: Value(idempotencyKey),
      );
}

String _jsonEncode(Map<String, dynamic> map) => jsonEncode(map);
Map<String, dynamic> _jsonDecode(String json) => jsonDecode(json) as Map<String, dynamic>;

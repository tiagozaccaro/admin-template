/// Flutter test for mobile sync (T079).
///
/// Tests the local drift SQLite database used for offline-first sync:
/// insert/query projects, drafts, and revisions, and clear on logout.

import 'package:flutter_test/flutter_test.dart';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:mobile/features/sync/sync_database.dart';

void main() {
  group("SyncDatabase", () {
    late SyncDatabase db;

    setUp(() {
      db = SyncDatabase.forTesting(NativeDatabase.memory());
    });

    tearDown(() async {
      await db.close();
    });

    test("inserts and queries a project", () async {
      await db.upsertProject(SyncProject(
        id: "proj-1",
        workspaceId: "ws-1",
        name: "Q3 Blog Series",
        createdBy: "user-1",
        createdAt: DateTime.parse("2026-01-01T00:00:00Z"),
      ));

      final projects = await db.getAllProjects();
      expect(projects, hasLength(1));
      expect(projects.first.name, "Q3 Blog Series");
      expect(projects.first.workspaceId, "ws-1");
    });

    test("inserts and queries a draft", () async {
      await db.upsertDraft(SyncDraft(
        id: "draft-1",
        contentItemId: "item-1",
        currentRevisionId: "rev-1",
        updatedAt: DateTime.parse("2026-01-01T00:00:00Z"),
      ));

      final drafts = await db.getAllDrafts();
      expect(drafts, hasLength(1));
      expect(drafts.first.contentItemId, "item-1");
      expect(drafts.first.currentRevisionId, "rev-1");
    });

    test("inserts and queries revisions for an entity", () async {
      await db.insertRevision(SyncContentRevision(
        id: "rev-1",
        entityType: "content_item",
        entityId: "item-1",
        revision: 1,
        authorId: "user-1",
        createdAt: DateTime.parse("2026-01-01T00:00:00Z"),
        payload: {"title": "Draft v1"},
        priorRevisionId: null,
      ));
      await db.insertRevision(SyncContentRevision(
        id: "rev-2",
        entityType: "content_item",
        entityId: "item-1",
        revision: 2,
        authorId: "user-1",
        createdAt: DateTime.parse("2026-01-02T00:00:00Z"),
        payload: {"title": "Draft v2"},
        priorRevisionId: "rev-1",
      ));

      final revisions = await db.getRevisionsForEntity("item-1");
      expect(revisions, hasLength(2));
      expect(revisions[0].revision, 1);
      expect(revisions[1].revision, 2);
      expect(revisions[1].priorRevisionId, "rev-1");
    });

    test("clear removes all data", () async {
      await db.upsertProject(SyncProject(
        id: "proj-1",
        workspaceId: "ws-1",
        name: "Project",
        createdBy: "user-1",
        createdAt: DateTime.parse("2026-01-01T00:00:00Z"),
      ));
      await db.upsertDraft(SyncDraft(
        id: "draft-1",
        contentItemId: "item-1",
        updatedAt: DateTime.parse("2026-01-01T00:00:00Z"),
      ));

      await db.clear();

      expect(await db.getAllProjects(), isEmpty);
      expect(await db.getAllDrafts(), isEmpty);
    });
  });
}

---
name: flutter-engineering
description: Flutter 3 (Dart SDK ^3.13) engineering for admin-template mobile app. Use when developing widgets, state, networking, tests, or platform integration in apps/mobile.
---

# Flutter Engineering

## Stack
- Flutter supported platforms: Android/iOS/macOS/Linux (workspace present).
- Dart SDK ^3.13.4, cupertino_icons, flutter_lints.
- Entry lib/main.dart; tests in test/widget_test.dart.

## Rules
- Keep widget trees small; extract widgets for readability and testability.
- Match analysis_options.yaml; fix analyzer findings before completion.
- Manage state cleanly; avoid side effects in build methods.
- Handle loading/error states for network-dependent UI.
- Ensure accessibility (semantics labels, responsive layout, keyboard).
- Format with `flutter format`, analyze with `flutter analyze`, test with `flutter test`.

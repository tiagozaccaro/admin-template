# Tasks: Test Coverage for Missing Application Tests

**Input**: Design documents from `/specs/004-test-coverage/`

**Tests**: This feature IS the tests.

## Phase 1: API

- [x] T001 [P] Add identity service tests in apps/api/tests/
  - [x] T001a Register/login/password-reset unit tests
  - [x] T001b Email verification token tests
- [x] T002 [P] Add tenancy service/router tests
  - [x] T002a Tenant CRUD tests
  - [x] T002b Membership/invitation tests
  - [x] T002c Cross-tenant denial tests
- [x] T003 [P] Add workspace tests
- [x] T004 [P] Add dashboard tests
- [x] T005 [P] Add items CRUD/IDOR tests
- [x] T006 [P] Add auth router tests
- [x] T007 [P] Add permissions deps tests
- [x] T008 [P] Add core utility tests (security, email, rate_limit)

## Phase 2: Web

- [x] T009 [P] Add page tests (login, signup, dashboard, items, tenants, account)
- [x] T010 [P] Add auth helper tests (session, google)
- [x] T011 [P] Add component tests (states, breadcrumbs)

## Phase 3: Mobile

- [x] T012 [P] Add auth service tests
- [x] T013 [P] Add screen widget tests

## Phase 4: Shared UI

- [x] T014 [P] Configure test runner for packages/ui
- [x] T015 [P] Add component tests for shared ui

## Phase 5: Polish

- [x] T016 Run all suites and verify coverage >=80%
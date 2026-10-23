<!--
Sync Impact Report
Version change: (none) -> 1.0.0
Modified principles: initial constitution replaced/consolidated with the 12-article project constitution provided by the user.
Added sections: Articles I-XII, Governing Principle, Scope/Governance discipline.
Removed sections: prior five-principle summary and Additional Constraints (folded into Articles).
Follow-up TODOs: RATIFICATION_DATE unknown (marked TODO).
-->

# Project Constitution — Reusable SaaS Foundation

## Article I — Preserve and Evolve the Existing Project

The existing repository is the starting point and source of truth.

- Preserve the current technology stack, architecture, directory structure, naming conventions, coding standards, and established workflows wherever practical.
- Before proposing changes, inspect the existing implementation, documentation, configuration, specifications, and tests.
- Prefer extending, improving, and integrating existing components over replacing them.
- Do not rewrite working functionality solely to match a preferred architecture, framework, library, or coding style.
- Existing project decisions remain valid unless evidence demonstrates a concrete problem or a requirement cannot reasonably be satisfied otherwise.

**Compatibility is the default, not an absolute restriction.**

## Article II — Merge with Existing Conventions

New requirements, specifications, and implementations must integrate with the project's existing conventions.

- Treat new specifications as additions to the existing project, not as a replacement constitution or a new project definition.
- Reconcile new requirements with existing specifications, architecture decisions, coding guidelines, and operational procedures before introducing changes.
- Preserve existing requirements unless they conflict with an explicitly approved change.
- When two requirements overlap, prefer a consistent implementation that satisfies both rather than duplicating functionality.
- When requirements conflict, document the conflict, its impact, and the proposed resolution before proceeding with consequential changes.
- Never silently discard, overwrite, or reinterpret existing project decisions.

If the repository already contains a constitution, amend and consolidate it rather than creating a competing set of principles.

## Article III — Evidence-Based Engineering

All significant engineering decisions must be grounded in the actual repository and verifiable requirements.

- Inspect relevant code before declaring functionality missing.
- Distinguish implemented, partially implemented, planned, mocked, and missing functionality.
- Support gap analyses with concrete repository evidence wherever possible.
- Avoid speculative requirements, unnecessary dependencies, and premature abstractions.
- Prefer the simplest maintainable solution that satisfies the required behavior.
- Document assumptions when evidence is incomplete.

## Article IV — Incremental and Reversible Change

Development must proceed through small, reviewable, testable increments.

- Divide work into clearly scoped implementation batches.
- Define acceptance criteria and dependencies before implementation.
- Avoid unrelated refactoring within feature changes.
- Keep changes localized unless broader changes are necessary and justified.
- Use feature flags, compatibility layers, or staged migrations when they materially reduce deployment risk.
- Preserve backward compatibility whenever practical.
- Explicitly document and obtain appropriate approval for unavoidable breaking changes.

## Article V — Modular Architecture

The project must remain maintainable and extensible as its functionality grows.

- Maintain clear module boundaries and separation of responsibilities.
- Reuse established abstractions before introducing new ones.
- Avoid unnecessary coupling between unrelated modules.
- Keep optional capabilities modular so they do not become mandatory dependencies of the core application.
- Introduce architectural changes only when they solve a demonstrated problem or satisfy an approved requirement.
- Do not introduce microservices, new frameworks, or additional infrastructure without a justified need.

## Article VI — Security and Data Integrity

Security and correctness are mandatory requirements, not optional enhancements.

- Enforce authorization at trusted server-side boundaries.
- Validate untrusted inputs and protect sensitive operations.
- Follow secure practices for authentication, sessions, secrets, and error handling.
- For multi-tenant functionality, enforce tenant isolation across APIs, data access, background jobs, and file operations.
- Apply least privilege to users, services, and administrative operations.
- Preserve existing data during migrations and provide appropriate rollback or recovery procedures.
- Never weaken established security controls to simplify implementation.
- Include automated verification for critical security and access-control requirements.

Security improvements must integrate with existing controls rather than introduce competing mechanisms.

## Article VII — Testing and Verifiable Quality

Every change must meet a level of verification appropriate to its risk. Tests are mandatory, not optional.

- Follow the repository's established testing framework and conventions.
- Add or update tests for ALL new and changed behavior, including happy paths, error paths, edge cases, and permission boundaries.
- Preserve existing tests unless their replacement is justified and equivalent or better coverage is maintained.
- Add regression tests for every bug fix that reproduce the defect before the fix.
- Aim for meaningful coverage (>=80% on changed code) and do not lower thresholds to pass.
- Use automated formatting, linting, type checking, and CI checks; they must pass before merge.
- Do not claim functionality is complete when required tests have not passed or verification has not been performed.
- Document blocked or unavailable verification explicitly.

## Article VIII — Specification and Traceability

Specifications must describe required behavior without unnecessarily prescribing implementation details.

- Every significant requirement must have clear, testable acceptance criteria.
- Link requirements to implementation tasks and relevant tests.
- Respect the repository's existing specification-driven development workflow.
- Avoid duplicate specifications and conflicting sources of truth.
- Keep documentation synchronized with material behavioral and architectural changes.
- Separate mandatory requirements from optional enhancements.
- Resolve significant ambiguities before implementation rather than relying on undocumented assumptions.

## Article IX — Git and Review Discipline

Changes must follow the repository's existing collaboration and delivery workflow.

- Follow existing branch naming, commit conventions, pull request templates, and merge policies.
- Keep implementation batches small enough for meaningful review.
- Associate pull requests with the requirements and tasks they address.
- Require applicable automated checks and review approvals before merging, according to repository policy.
- Preserve traceability between specifications, issues, pull requests, and tests.
- Never bypass required checks or branch protections merely to complete a task faster.
- Do not modify unrelated files or include unrelated changes in a pull request.

If the project already defines a workflow, integrate with it rather than introducing a competing process.

## Article X — Controlled Dependencies and Operational Reliability

New dependencies and infrastructure must provide measurable value.

- Prefer existing project dependencies and established platform capabilities.
- Evaluate maintenance, security, licensing, compatibility, operational cost, and vendor lock-in before adding significant dependencies.
- Keep secrets out of source control.
- Follow existing environment and configuration conventions.
- Preserve deployment compatibility and document required configuration changes.
- Include appropriate observability, error handling, and recovery considerations for production-critical changes.
- Avoid introducing paid services or infrastructure without explicit justification and approval where required.

## Article XI — Pragmatic SaaS Foundations

For SaaS-specific capabilities, prioritize correctness and reuse over unnecessary complexity.

- Design tenant boundaries and authorization explicitly when multi-tenancy is required.
- Keep authentication, organizations, permissions, billing, notifications, auditing, and platform administration logically separated according to the existing architecture.
- Make optional capabilities optional.
- Implement billing, AI, plugins, advanced analytics, and enterprise functionality only when required by approved specifications.
- Avoid building a generic framework for hypothetical future requirements.
- Ensure foundational capabilities can be extended without requiring a rewrite of the application.

These principles guide decisions but do not mandate a particular programming language, framework, database, hosting provider, or SaaS business model.

## Article XII — Conflict Resolution and Amendments

When a new requirement conflicts with the current project:

1. Identify the existing decision and the new requirement.
2. Determine whether both can be satisfied through integration, extension, or a localized adaptation.
3. If not, explain the alternatives, trade-offs, migration impact, and risks.
4. Recommend the least disruptive option that satisfies the approved requirement.
5. Obtain the required approval before making consequential architectural changes or removing established functionality.
6. Update affected specifications, documentation, and tests after the decision is made.

This constitution may evolve as the project evolves. Amendments must be deliberate, documented, and consistent with existing project governance.

## Governing Principle

**Extend before replacing. Integrate before duplicating. Verify before assuming. Refactor when justified. Preserve what works.**

The objective is to evolve the existing project into a reliable, maintainable, reusable SaaS foundation while retaining its valuable design decisions, working functionality, and established development workflow.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date unknown | **Last Amended**: 2026-10-23
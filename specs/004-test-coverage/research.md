# Research: Test Coverage

## Decisions

- **API**: reuse pytest + existing fixtures; mock email/OIDC providers.
- **Web**: vitest + testing-library (already configured).
- **Mobile**: flutter test widget tests.
- **Shared UI**: add vitest + @testing-library/react to packages/ui.
- **Coverage target**: >=80% on changed code; reuse existing thresholds.
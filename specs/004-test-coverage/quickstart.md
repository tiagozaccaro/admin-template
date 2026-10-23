# Quickstart: Test Coverage

## Prerequisites
- Node 22+, pnpm
- Python 3.12, uv
- Flutter 3.x

## Run tests

API:
```
cd apps/api && uv run pytest
```

Web:
```
pnpm --filter @admin-template/web test
pnpm --filter @admin-template/web typecheck
```

Mobile:
```
cd apps/mobile && flutter test
```

Shared UI:
```
pnpm --filter @admin-template/ui test
```

## Expected
All suites pass; coverage on changed code >=80%.
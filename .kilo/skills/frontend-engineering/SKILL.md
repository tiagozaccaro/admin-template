---
name: frontend-engineering
description: Frontend engineering for Next.js 16, React 19, TypeScript, Tailwind 4, and shadcn/ui in admin-template web/ui packages. Use when building or fixing React components, routing, data fetching, forms, accessibility, or styling.
---

# Frontend Engineering

## Stack
- Next.js 16.4 App Router, React 19.3, strict TypeScript 5.
- Tailwind CSS 4, shadcn registry, Base UI primitives, lucide icons, recharts, zod.
- Shared component library in packages/ui; web app consumes via workspace dependency.
- ESLint/Prettier configs from @workspace/eslint-config.

## Rules
- App Router only. Server Components by default; add `"use client"` only for browser APIs or client state.
- Keep files under 300 lines; split when complexity grows.
- Use zod for input/schema validation at boundaries.
- UI must be accessible: semantic elements, keyboard navigation, focus states, labels, color contrast.
- Use shadcn components and Tailwind tokens; no ad-hoc inline styles unless justified.
- Strict TypeScript: no `any`; explicit types for component props, hooks, returned data.
- Handle loading and error states in routes/data fetching.
- Run `pnpm --filter @admin-template/web typecheck lint` and build when affected.

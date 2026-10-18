# @workspace/api-client

Generated OpenAPI client for the Admin Template FastAPI API.

This package is populated by OpenAPI client generation from the API's
OpenAPI schema. It is consumed by the web and mobile clients; no client
may bypass the FastAPI API to mutate state directly.

## Generation

Run the OpenAPI generator against the FastAPI OpenAPI schema to regenerate
this package:

```bash
pnpm --filter api-client generate
```

## Usage

Import generated API clients from `@workspace/api-client`:

```ts
import { ApiClient } from "@workspace/api-client";
```

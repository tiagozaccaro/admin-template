# Data Model: Admin Template Product

## Entities

### User
- id (uuid, PK)
- email (unique, not null)
- display_name
- profile_image_url
- created_at, updated_at
- deleted_at (nullable)

### ExternalIdentity
- id (uuid, PK)
- user_id (FK User)
- provider (string, e.g. "google")
- provider_subject (string, unique per provider)
- email (provider-reported)
- linked_at
- UNIQUE(provider, provider_subject)

### Session
- id (uuid, PK)
- user_id (FK User)
- token_hash (unique)
- expires_at
- revoked_at (nullable)
- created_at
- client_type (web/mobile)

### Tenant
- id (uuid, PK)
- name
- slug (unique)
- branding (json)
- created_at, updated_at
- owner_user_id (FK User)

### TenantMembership
- id (uuid, PK)
- user_id (FK User)
- tenant_id (FK Tenant)
- role (enum: owner/admin/member/viewer)
- created_at
- UNIQUE(user_id, tenant_id)

### Invitation
- id (uuid, PK)
- tenant_id (FK Tenant)
- email
- role
- token_hash (unique)
- expires_at
- accepted_at (nullable)
- revoked_at (nullable)
- created_by (FK User)
- created_at

### UserPreferences
- user_id (PK, FK User)
- theme (light/dark/system)
- locale
- updated_at

### TenantSettings
- tenant_id (PK, FK Tenant)
- metadata (json)
- updated_at

### Notification
- id (uuid, PK)
- tenant_id (FK Tenant)
- user_id (FK User, nullable for tenant-wide)
- title, body
- read_at (nullable)
- created_at

### AuditEvent
- id (uuid, PK)
- tenant_id (FK Tenant, nullable for global)
- actor_user_id (FK User, nullable)
- action (string)
- target_type, target_id
- result_summary
- created_at
- INDEX(tenant_id, created_at)

### AIConversation
- id (uuid, PK)
- tenant_id (FK Tenant)
- user_id (FK User)
- title
- created_at, updated_at

### AIMessage
- id (uuid, PK)
- conversation_id (FK AIConversation)
- role (user/assistant/system/tool)
- content (text)
- created_at

### AIToolExecution
- id (uuid, PK)
- conversation_id (FK AIConversation)
- tool_name
- arguments (json)
- status (pending/approved/executed/failed/rejected)
- result_summary
- approved_by (FK User, nullable)
- created_at

## Relationships
- User 1..* ExternalIdentity
- User 1..* Session
- User *..* Tenant via TenantMembership
- Tenant 1..* Invitation
- Tenant 1..* Notification
- Tenant 1..* AuditEvent
- User 1..1 UserPreferences
- Tenant 1..1 TenantSettings
- User 1..* AIConversation (tenant-scoped)
- AIConversation 1..* AIMessage
- AIConversation 1..* AIToolExecution

## Tenant scope
Every tenant-owned entity carries tenant_id and is filtered by validated membership. Cross-tenant access fails closed.

## Indexing
- memberships: (user_id), (tenant_id)
- invitations: (tenant_id), (token_hash)
- notifications: (user_id, read_at), (tenant_id, created_at)
- audit_events: (tenant_id, created_at)
- ai_conversations: (tenant_id, user_id)
- ai_messages: (conversation_id, created_at)

# Evident Technologies Cross-Platform Architecture

## N-Tier Architecture with Strict Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Evident.Web  │  │ Evident.Mobile│  │ MatterDocket │     │
│  │   (ASP.NET)  │  │    (MAUI)     │  │    (MAUI)    │     │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────┘     │
│         │                  │                   │             │
└─────────┼──────────────────┼───────────────────┼─────────────┘
          │                  │                   │
          │                  └───────┬───────────┘
          │                          │
┌─────────▼──────────────────────────▼─────────────────────────┐
│               INFRASTRUCTURE LAYER (Optional)                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          Evident.Infrastructure                        │  │
│  │  • Data Access (EF Core, SQLite)                       │  │
│  │  • Repository Implementations                          │  │
│  │  • External Service Integrations                       │  │
│  └────────────────────┬───────────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────────┐
│                   DOMAIN/SHARED LAYER                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Evident.Shared (Core)                     │  │
│  │  • Domain Models (Case, User, AnalysisRequest)        │  │
│  │  • DTOs (Data Transfer Objects)                        │  │
│  │  • Service Interfaces (IApiClient)                     │  │
│  │  • Business Rules & Validations                        │  │
│  │  • Constants & Enums                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                   ↑ NO DEPENDENCIES ↑                         │
└──────────────────────────────────────────────────────────────┘
```

## Tier Boundaries & Dependencies

### ✅ ALLOWED Dependencies (Top-Down Only)

```
Web → Infrastructure → Shared
Mobile → Shared (bypasses Infrastructure for offline-first)
MatterDocket.MAUI → Shared
```

### ❌ FORBIDDEN Dependencies

```
Shared ✗→ Infrastructure
Shared ✗→ Web
Shared ✗→ Mobile
Infrastructure ✗→ Web
Infrastructure ✗→ Mobile
```

## Layer Responsibilities

### 1. **Evident.Shared** (Core Domain)

**Target:** `.NET 9` (Standard library) **Purpose:** Platform-agnostic domain
logic

**Contains:**

- ✅ Domain entities (`Case`, `User`, `AnalysisRequest`)
- ✅ DTOs for API communication
- ✅ Service interfaces (`IApiClient`, `IAuthService`)
- ✅ Business validation attributes
- ✅ Enums and constants

**Must NOT contain:**

- ❌ Database code (EF Core entities)
- ❌ UI code (Views, ViewModels)
- ❌ Platform-specific code
- ❌ External service implementations

### 2. **Evident.Infrastructure** (Data Access)

**Target:** `.NET 9` **Purpose:** Data persistence and external integrations

**Contains:**

- ✅ EF Core DbContext
- ✅ Repository implementations
- ✅ Database migrations
- ✅ External API clients (concrete implementations)
- ✅ Caching strategies

**Dependencies:**

- ✅ References `Evident.Shared`
- ✅ EF Core packages
- ✅ Database drivers (SQLite, SQL Server)

### 3. **Evident.Web** (Web API)

**Target:** `.NET 9` **Purpose:** RESTful API and web services

**Contains:**

- ✅ Controllers
- ✅ Middleware
- ✅ Authentication/Authorization
- ✅ API versioning
- ✅ Swagger/OpenAPI

**Dependencies:**

- ✅ References `Evident.Infrastructure`
- ✅ References `Evident.Shared`
- ✅ ASP.NET Core packages

### 4. **Evident.Mobile** (MAUI App)

**Target:** `.NET 10` (MAUI multi-targeting) **Purpose:** Cross-platform mobile
app

**Contains:**

- ✅ XAML Views
- ✅ ViewModels (MVVM pattern)
- ✅ Platform-specific services
- ✅ Local SQLite storage
- ✅ Offline-first logic

**Dependencies:**

- ✅ References `Evident.Shared` ONLY
- ✅ MAUI packages
- ✅ CommunityToolkit.Mvvm
- ✅ sqlite-net-pcl (local storage)

**Why no Infrastructure reference:**

- Mobile apps need lightweight, offline-first architecture
- Direct API calls via `IApiClient` in Shared
- Local storage using sqlite-net-pcl (not EF Core)

### 5. **Evident.MatterDocket.MAUI** (Legal Docket App)

**Target:** `.NET 10` (MAUI multi-targeting) **Purpose:** Specialized legal
matter management

**Contains:**

- ✅ Matter-specific Views
- ✅ Legal workflow ViewModels
- ✅ Document management UI
- ✅ Court date tracking

**Dependencies:**

- ✅ References `Evident.Shared` ONLY
- ✅ Same pattern as Mobile

## Design Principles

### 1. **Dependency Inversion Principle**

- High-level modules (Web, Mobile) depend on abstractions (Shared)
- Low-level modules (Infrastructure) implement abstractions
- Shared layer defines interfaces, Infrastructure implements them

### 2. **Separation of Concerns**

- **Presentation:** UI logic only
- **Domain:** Business rules only
- **Data:** Persistence only

### 3. **Platform Independence**

- Shared layer has NO platform-specific code
- Mobile apps can work offline
- Web API can scale independently

### 4. **Testability**

- Each layer can be tested in isolation
- Shared layer has no external dependencies
- Interfaces enable mocking

## Testing Strategy

```
Evident.Shared.Tests          → Unit tests for domain logic
Evident.Infrastructure.Tests  → Integration tests with real DB
Evident.Web.Tests             → API integration tests
Evident.Mobile.Tests          → UI and ViewModel tests
```

## Data Flow Examples

### Example 1: User Login (Web API)

```
User → Web.Controller
    → Infrastructure.AuthRepository (DB check)
    → Shared.User (domain model)
    → Web.Controller (JWT token)
    → User
```

### Example 2: Case Analysis (Mobile - Offline)

```
User → Mobile.View
    → Mobile.ViewModel
    → Shared.IApiClient (interface)
    → Mobile.Services.ApiClientImpl (HTTP or local cache)
    → Shared.Case (domain model)
    → Mobile.ViewModel
    → Mobile.View (display)
```

### Example 3: Case Sync (Mobile to Web)

```
Mobile.LocalDB (SQLite)
    → Mobile.ViewModel
    → Shared.IApiClient.SyncCases()
    → Web.API.CasesController
    → Infrastructure.CaseRepository
    → Database (SQL Server)
```

## Migration Path

If you currently have violations:

1. **Move domain models to Shared:**

   ```bash
   mv Infrastructure/Models/*.cs Shared/Models/
   ```

2. **Extract interfaces to Shared:**

   ```csharp
   // Shared/Services/IApiClient.cs
   public interface IApiClient
   {
       Task<List<Case>> GetCasesAsync();
   }

   // Mobile/Services/ApiClient.cs (implementation)
   public class ApiClient : IApiClient { }
   ```

3. **Remove circular dependencies:**
   - Check with: `dotnet list package --include-transitive`
   - Ensure Shared has NO project references

## Build Verification

Run these commands to verify architecture:

```bash
# Verify Shared has no dependencies
cd src/Evident.Shared
dotnet list reference
# Expected: (empty)

# Verify Infrastructure depends only on Shared
cd ../Evident.Infrastructure
dotnet list reference
# Expected: Evident.Shared

# Verify Web depends on Infrastructure and Shared
cd ../Evident.Web
dotnet list reference
# Expected: Evident.Infrastructure, Evident.Shared

# Verify Mobile depends only on Shared
cd ../Evident.Mobile
dotnet list reference
# Expected: Evident.Shared
```

## Common Anti-Patterns to Avoid

❌ **Shared depending on Infrastructure**

```xml
<!-- WRONG in Shared.csproj -->
<ProjectReference Include="..\Infrastructure\Infrastructure.csproj" />
```

❌ **Mobile depending on Infrastructure**

```xml
<!-- WRONG in Mobile.csproj -->
<ProjectReference Include="..\Infrastructure\Infrastructure.csproj" />
```

❌ **Concrete types in Shared**

```csharp
// WRONG in Shared layer
public class SqlCaseRepository  // Concrete implementation!
{
    private readonly DbContext _db;  // EF Core dependency!
}
```

✅ **Correct: Interface in Shared**

```csharp
// RIGHT in Shared layer
public interface ICaseRepository
{
    Task<List<Case>> GetAllAsync();
}

// Implementation in Infrastructure
public class SqlCaseRepository : ICaseRepository
{
    private readonly AppDbContext _db;
    // ...
}
```

## Summary

**Architecture Goals:** ✅ Strict tier boundaries enforced at compile-time ✅
Platform-independent core (Shared layer) ✅ Mobile apps work offline with local
storage ✅ Web API can scale independently ✅ All layers independently testable
✅ Dependency Inversion Principle followed

**Key Rules:**

1. Shared has ZERO dependencies
2. Mobile/MAUI apps depend ONLY on Shared
3. Web depends on Infrastructure + Shared
4. Infrastructure depends ONLY on Shared
5. Dependencies flow ONE WAY (down the stack)

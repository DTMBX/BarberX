# Third-Party License Attribution

This document provides detailed licensing information for all third-party dependencies used in the Geneva Bible Study Platform.

## 📋 Summary

All dependencies in this project use permissive, non-attributable open source licenses that allow:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ✅ No attribution requirements (beyond license preservation)

## 🔑 License Categories

### MIT License
The most permissive and widely-used license. Requires only preservation of copyright notice.

**Core Framework & Build Tools:**
- React (Facebook, Inc.)
- React DOM (Facebook, Inc.)
- Vite (Yuxi Evan You)
- TypeScript ESLint (TypeScript ESLint Team)

**UI Libraries:**
- @radix-ui/* (all Radix UI packages)
- @phosphor-icons/react (Phosphor Icons)
- lucide-react (Lucide)
- class-variance-authority
- clsx
- tailwind-merge
- cmdk
- vaul
- sonner
- input-otp
- react-day-picker
- embla-carousel-react

**State & Data Management:**
- @tanstack/react-query (TanStack)
- react-hook-form (React Hook Form)
- zod (Colin McDonnell)
- date-fns (Sasha Koss)

**Animation & Interaction:**
- framer-motion (Framer)

**Development Tools:**
- @vitejs/plugin-react-swc
- @tailwindcss/vite
- @tailwindcss/postcss
- eslint (OpenJS Foundation)
- eslint-plugin-react-hooks
- eslint-plugin-react-refresh

**Utilities:**
- uuid
- marked
- d3 (Mike Bostock)

### Apache License 2.0
Permissive license similar to MIT with explicit patent grant.

**Language & Type System:**
- TypeScript (Microsoft Corporation)

### ISC License
Functionally equivalent to MIT, even more permissive.

**Dependencies:**
- Various transitive dependencies

### BSD Licenses
Permissive licenses with minimal restrictions.

**Dependencies:**
- Various transitive dependencies

## 📚 Bible API License

### Bolls Life Bible API
- **License:** Public Domain
- **Attribution Required:** NO
- **API Key Required:** NO
- **Rate Limits:** None
- **Commercial Use:** Allowed
- **Content License:** All Bible translations are Public Domain

**Available Translations:**
All 16+ translations provided by the API are in the Public Domain:
- Geneva Bible (1560)
- King James Version (1611)
- World English Bible (2000)
- Young's Literal Translation (1862)
- American Standard Version (1901)
- And 11+ more...

See [BIBLE_API_INTEGRATION.md](./BIBLE_API_INTEGRATION.md) for complete list.

## 🎨 Font Licenses

### Google Fonts
All fonts used are licensed under the SIL Open Font License 1.1, which allows:
- Free commercial and non-commercial use
- Modification and redistribution
- Embedding in applications and websites

**Fonts Used:**
- **Crimson Pro** - SIL OFL 1.1
- **Literata** - SIL OFL 1.1
- **JetBrains Mono** - SIL OFL 1.1

## 🔍 License Verification

### How to Verify Licenses

You can verify the license of any package using:

```bash
npm view <package-name> license
```

Example:
```bash
npm view react license          # Returns: MIT
npm view typescript license     # Returns: Apache-2.0
npm view @phosphor-icons/react license  # Returns: MIT
```

### Generate Complete License Report

To generate a complete license report for all dependencies:

```bash
npx license-checker --summary
```

To see detailed information:

```bash
npx license-checker --json > licenses.json
```

## ⚖️ License Compliance Checklist

- [x] All dependencies use permissive open source licenses
- [x] No GPL or copyleft licenses that would require source disclosure
- [x] No proprietary or commercial licenses requiring payment
- [x] No dependencies requiring mandatory attribution in UI
- [x] All Bible text content is Public Domain
- [x] No API keys or authentication required for core functionality
- [x] Application can be deployed to any hosting service
- [x] Source code can be freely modified and redistributed

## 📦 Production Build License Files

When building for production, the following license information is preserved:

1. **Project LICENSE file** - MIT License for the application code
2. **Package metadata** - License information in package.json
3. **Third-party notices** - Preserved in bundled code comments

## 🚫 Excluded Licenses

The following license types are **NOT** used in this project:

- ❌ GNU GPL (General Public License) - Copyleft, requires source disclosure
- ❌ GNU AGPL (Affero GPL) - Network copyleft, very restrictive
- ❌ SSPL (Server Side Public License) - Requires cloud provider source disclosure
- ❌ Proprietary/Commercial licenses requiring purchase
- ❌ Creative Commons Non-Commercial (CC BY-NC) - Restricts commercial use
- ❌ Creative Commons No-Derivatives (CC BY-ND) - Restricts modification

## 📝 Attribution Requirements

While most licenses don't require UI attribution, proper attribution should be maintained:

### Required in Source Code
- Preserve LICENSE file in repository root
- Maintain copyright notices in source files
- Keep package.json license metadata

### NOT Required in Application UI
- No "Powered by" badges required
- No mandatory attribution footer
- No splash screen requirements
- No startup notices

### Recommended (Optional)
- Acknowledge key libraries in About section
- Link to Bolls Life API in API documentation
- Credit font designers in design documentation

## 🔄 License Updates

Licenses are checked during:
- **Dependency updates:** Dependabot runs weekly
- **New package installations:** Review license before adding
- **Security audits:** `npm audit` includes license checks

## 📞 Questions About Licenses?

If you have questions about licensing:

1. Check the specific package's LICENSE file: `node_modules/<package>/LICENSE`
2. Visit the package's repository (listed in package.json)
3. Use `npm view <package> homepage` to find official documentation
4. Contact the package maintainers for clarification

## 🎯 Deployment Considerations

### Self-Hosting
- ✅ No license restrictions for self-hosting
- ✅ Can deploy to any infrastructure (cloud or on-premise)
- ✅ Can modify and customize freely

### SaaS/Cloud Deployment
- ✅ Can deploy as a service without source disclosure
- ✅ No AGPL restrictions
- ✅ Can charge for hosting/access (application is MIT)

### White-Label/Rebranding
- ✅ Can rebrand and resell (maintain license notices in source)
- ✅ Can integrate into larger applications
- ✅ Can modify for specific use cases

## 📅 Last Updated

License review last performed: January 2025

Review frequency: With every dependency update via Dependabot

---

**Note:** This document provides a summary of licensing information. For complete legal details, refer to the LICENSE file in each dependency's package directory and consult with legal counsel for specific use cases.

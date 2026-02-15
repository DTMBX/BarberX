# Changelog

All notable changes to the Geneva Bible Study Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### 🎉 Initial Release

A comprehensive Bible study platform with scholarly features and social engagement.

### Added

#### Core Reading Features
- **Multi-Translation Bible Reader** - Read Scripture in 16+ public domain translations
- **Geneva Bible Primary Text** - Featured as default translation with historical significance
- **Translation Comparison** - Side-by-side view with synchronized scrolling (up to 6 translations)
- **Translation Presets** - Save favorite translation combinations for quick access
- **Verse Navigation** - Jump to any book, chapter, or verse instantly
- **Reading Position** - Auto-saves last reading location

#### Audio Bible Features
- **Audio Playback** - Listen to Scripture with Web Speech Synthesis
- **Multiple Narrators** - Choose from 4+ distinct voices (male/female, accents)
- **Voice Preview** - Test narrators before selecting
- **Playback Controls** - Speed (0.5x-2.0x), volume, play/pause/stop
- **Verse Highlighting** - Visual highlighting of currently playing verse
- **Audio Bookmarks** - Save favorite audio moments with metadata
- **Voice Annotations** - Record personal reflections on passages (up to 5 minutes)
- **AI Transcription** - Convert voice annotations to searchable text notes
- **Editable Transcriptions** - Refine AI-generated transcriptions for accuracy

#### Reading Plans
- **Structured Plans** - One Year, 90 Days NT, Chronological, and more
- **Custom Plans** - Create personalized plans with selected books and chapters
- **Progress Tracking** - Monitor completion percentage and reading streaks
- **Calendar View** - Visual overview of daily readings and completion status
- **Direct Reading** - Click any chapter to open in Bible Reader
- **Daily Reminders** - Configurable notifications at preferred times

#### Social Features
- **Friend System** - Connect with others' reading journeys
- **Friend Requests** - Send and accept connection requests
- **Reading Profiles** - View friends' current books, plans, streaks, and milestones
- **Private Messaging** - Discuss verses and passages with friends
- **Verse Sharing** - Share favorite verses directly in messages with formatting
- **Group Discussions** - Collaborative Bible study with multiple participants
- **Message Reactions** - React with emojis (👍 ❤️ 🙏 🔥)
- **Message Pinning** - Pin important messages in groups
- **Message Editing** - Edit and delete your messages
- **Role-Based Permissions** - Admin, Moderator, and Member roles with granular permissions
- **Group Settings** - Control posting permissions, member invites, and moderation
- **Unread Badges** - Clear notification counts for pending requests, messages, and groups

#### Verse of the Day
- **Daily Verse** - Automatically rotates through inspirational passages
- **Translation Selector** - View in any available translation
- **Translation Comparison** - See verse in up to 6 translations side-by-side
- **Sharing Options** - Share with friends or groups
- **Context Reading** - Jump to full chapter from verse
- **Scheduled Notifications** - Daily reminders at user-selected times
- **Like/Favorite** - Mark meaningful verses

#### Search & Discovery
- **Full-Text Search** - Search across all downloaded translations
- **Timeline View** - Interactive historical timeline of biblical events
- **Library Navigator** - Browse Bible as organized collection of books
- **Book Categories** - Law, History, Wisdom, Prophets, Gospels, Epistles, more

#### Accessibility Features
- **Dark Mode** - Manual toggle and automatic scheduling
- **Sunset/Sunrise Scheduling** - Location-based automatic theme switching
- **Custom Schedule** - Set specific daily times for dark mode
- **Voice-to-Text Messaging** - Record messages with AI transcription
- **Keyboard Shortcuts** - Complete keyboard navigation (Ctrl+D, Ctrl+K, 1-9)
- **Screen Reader Support** - Proper ARIA labels and semantic HTML
- **Adjustable Typography** - Font size, family, line spacing controls
- **High Contrast Support** - WCAG AA compliant color contrast

#### User Experience
- **Offline Support** - Download translations for offline study
- **KV Persistence** - All user data stored locally in browser
- **Responsive Design** - Optimized for mobile and desktop
- **Progressive Web App** - Install as standalone app
- **Fast Performance** - Vite build with optimized assets
- **Beautiful Typography** - Crimson Pro, Literata, JetBrains Mono fonts
- **Smooth Animations** - Framer Motion for purposeful transitions

### Technical

#### Architecture
- **React 19** - Latest React with modern hooks
- **TypeScript** - Full type safety throughout
- **Vite 7** - Lightning-fast build tool
- **Tailwind CSS 4** - Utility-first styling with custom theme
- **shadcn/ui** - 40+ accessible UI components (Radix UI primitives)
- **Phosphor Icons** - Comprehensive icon library (2000+ icons)
- **Framer Motion** - Smooth animations
- **KV Storage** - Browser-based persistence via Spark SDK

#### API Integration
- **Bolls Life Bible API** - Public domain Bible text
- **16+ Translations** - Full Old & New Testament coverage
- **No API Key Required** - Free unlimited access
- **No Attribution Required** - Public domain content
- **Automatic Caching** - Minimize API calls and enable offline

#### Deployment Ready
- **GitHub Actions Workflow** - Automated deployment to GitHub Pages
- **Multi-Platform Support** - Deploy to Vercel, Netlify, Firebase, AWS, self-hosted
- **Docker Support** - Containerized deployment option
- **Environment Configuration** - Easy customization for different environments
- **License Compliance** - All dependencies use permissive MIT/Apache licenses
- **Security Hardened** - No secrets, no authentication, client-side only

### Documentation

- **README.md** - Quick start and feature overview
- **PRD.md** - Complete product requirements document
- **BIBLE_API_INTEGRATION.md** - Detailed API documentation with examples
- **DEPLOYMENT.md** - Comprehensive deployment guide for all platforms
- **CONTRIBUTING.md** - Developer contribution guidelines
- **THIRD_PARTY_LICENSES.md** - Complete license attribution for all dependencies
- **SECURITY_POLICY.md** - Security best practices and reporting
- **CHANGELOG.md** - Version history and release notes

### Dependencies

All dependencies use permissive open source licenses (MIT, Apache 2.0, ISC):

**Core:** React 19, TypeScript 5.7, Vite 7  
**UI:** Radix UI, Tailwind CSS 4, Phosphor Icons, Framer Motion  
**Data:** TanStack Query, React Hook Form, Zod, date-fns  
**Dev Tools:** ESLint, TypeScript ESLint, SWC

See [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) for complete attribution.

## Future Roadmap

### Planned Features (v1.1+)

- **Data Export/Import** - Backup and restore user data
- **Advanced Search** - Boolean operators, phrase search, filters
- **Study Tools** - Commentaries, cross-references, concordance
- **Note Templates** - Pre-formatted note structures
- **Study Groups** - Scheduled group study sessions
- **Progress Analytics** - Reading statistics and insights
- **Custom Themes** - User-created color schemes
- **Multi-Device Sync** - Optional cloud backup (privacy-focused)

### Under Consideration

- **Mobile Apps** - Native iOS and Android versions
- **Offline-First Architecture** - Complete offline functionality
- **Additional Translations** - Expand beyond current 16
- **Original Language Tools** - Hebrew and Greek word studies
- **Historical Maps** - Biblical geography visualization
- **Audio Narration Quality** - Professional voice recordings
- **Community Features** - Public study groups, discussion forums

## Breaking Changes

None (initial release)

## Known Issues

- Voice annotations limited to browser-supported audio formats
- AI transcription quality varies with recording clarity
- Large Bible books (Psalms 119) may have slower initial load
- Social features require users to manually exchange profile connections

## Migration Guide

None (initial release)

## Contributors

Thank you to all contributors who helped build this platform!

- Core development team
- Beta testers and early adopters
- Open source community for amazing tools
- Bolls Life for providing free Bible API

## Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/YOUR_REPO/discussions)
- **Documentation:** See repository docs folder

---

**Note:** Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub repository details.

[1.0.0]: https://github.com/YOUR_USERNAME/YOUR_REPO/releases/tag/v1.0.0

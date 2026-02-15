# Audio Bible Enhancement Documentation

## New Audio Features

This document describes the enhanced audio Bible features including sleep timer, background playback, and playlist support.

## Features Added

### 1. Sleep Timer

The sleep timer allows users to set a duration after which audio playback will automatically stop. This is perfect for bedtime listening.

**Features:**
- Multiple preset durations: 5, 10, 15, 30, 45, 60, and 90 minutes
- Live countdown display showing remaining time
- Visual indicator (moon icon) when timer is active
- Can be canceled at any time
- Timer persists across chapter changes

**Usage:**
1. Open the Audio player in the Reader view
2. Click the Timer button (clock icon)
3. Select desired duration from the dropdown
4. The timer will countdown and stop playback automatically
5. To cancel, click the Timer button and select "Off"

**Location:** `AudioPlayerControls` component → Timer button (Popover)

### 2. Background Audio Playback

Background playback allows audio to continue playing when:
- Switching between tabs in the application
- The screen is locked (on supported devices)
- The browser tab is not in focus

**Technical Implementation:**
- Uses the Wake Lock API to prevent screen sleep during playback
- Automatically requests wake lock when audio starts playing
- Releases wake lock when audio stops
- Gracefully degrades on devices without Wake Lock API support

**User Preferences:**
- Background playback is enabled by default
- Preference is stored in `audio-preferences` with key `backgroundPlaybackEnabled`

### 3. Audio Playlists

Users can create custom playlists to listen to multiple chapters sequentially across different books.

**Features:**
- Create custom playlists with any combination of chapters
- Quick-create templates:
  - **Four Gospels**: All chapters from Matthew, Mark, Luke, and John
  - **Key Epistles**: Romans, 1 Corinthians, Galatians, Ephesians, Philippians, Colossians, James
  - **All Psalms**: Complete book of Psalms (150 chapters)
- Reorder chapters within a playlist (up/down arrows)
- Add current chapter to a new playlist
- Delete playlists
- Visual progress indicator showing current position in playlist
- Auto-advance to next chapter in playlist

**Creating a Custom Playlist:**
1. Click the "Playlists" button in the Reader toolbar
2. Click "Create Custom Playlist"
3. Enter a name and optional description
4. Add chapters by:
   - Clicking "Add Current Chapter" (when in Reader view)
   - Or use quick-create templates
5. Reorder chapters as desired using arrow buttons
6. Click "Create Playlist"

**Playing a Playlist:**
1. Open the Playlists dialog
2. Click the Play button on any playlist
3. Audio player opens and begins playback
4. When a chapter finishes, the next chapter automatically loads and plays
5. Current playlist and position shown in the audio player

**Location:** 
- Dialog: `PlaylistDialog` component
- Button: Reader toolbar → "Playlists" button
- Storage: Playlists stored in `audio-playlists` KV store

## Data Persistence

All audio preferences and playlists are stored using the Spark KV store:

- `audio-preferences`: User preferences including narrator, speed, volume, sleep timer defaults, background playback setting
- `audio-playlists`: Array of all user-created playlists

## Technical Architecture

### Hook: `useAudioBible`

Enhanced with new features:
- `setSleepTimer(minutes)`: Set or clear sleep timer
- `loadPlaylist(playlist)`: Load a playlist and start at position 0
- `advancePlaylist()`: Move to next chapter in playlist
- `nextInPlaylist()`: Get next playlist item without advancing
- Wake Lock management for background playback

### Components

1. **AudioPlayerControls**: Enhanced with sleep timer button and playlist indicator
2. **PlaylistDialog**: Complete playlist management UI
3. **ReaderView**: Integrated with playlist navigation events

### Events

- `playlist-advance`: Fired when moving to next chapter in playlist
  - Detail: `{ bookId: string, chapter: number }`
  - Triggers automatic navigation and resume playback

## Browser Compatibility

- **Wake Lock API**: Supported in Chrome 84+, Edge 84+, Safari 16.4+
- **Speech Synthesis**: Widely supported across all modern browsers
- **Graceful Degradation**: Features degrade gracefully on unsupported browsers

## Future Enhancements

Potential improvements for future iterations:
- Shuffle mode for playlists
- Repeat mode (repeat chapter, repeat playlist)
- Download playlists for offline listening
- Share playlists with friends
- Import/export playlists
- Smart playlists based on reading plans
- Cross-device playlist sync
- Sleep timer fade-out effect

# Windows Desktop Widget Guide

This guide explains how to create and use a Windows desktop widget for Geneva Bible Study, providing quick access to Bible verses, reading plans, and daily devotionals directly from your desktop.

## 🪟 Windows Desktop Widget Options

### Option 1: PWA Installation (Recommended - Easy Setup)

#### Install as Desktop App
1. **Using Microsoft Edge** (Recommended):
   - Open the Geneva Bible Study website in Edge
   - Click the **⋯** menu (top-right)
   - Select **Apps** → **Install Geneva Bible Study**
   - App installs as a standalone desktop application
   - Pin to taskbar for quick access

2. **Using Google Chrome**:
   - Open the site in Chrome
   - Click the **install icon** (➕) in the address bar
   - Or: Menu → **Install Geneva Bible Study**
   - App appears in Start Menu and taskbar

#### PWA Widget Features
- ✅ Native window (no browser UI)
- ✅ Taskbar icon
- ✅ Start menu entry
- ✅ Runs independently from browser
- ✅ Full offline support
- ✅ Automatic updates
- ✅ System notifications
- ✅ Always-on-top option (via Windows)

#### Make it a Desktop Widget
After installation:
1. Right-click the app window
2. Select **Always on Top** (via PowerToys or similar)
3. Resize to widget size (e.g., 400x600px)
4. Position on your desktop
5. Access anytime with taskbar click

---

### Option 2: Electron Desktop Application (Advanced - Native Features)

**Coming Soon**: Standalone Windows executable with enhanced desktop integration.

#### Planned Features
- Native window controls
- System tray integration
- Auto-start with Windows
- Better offline capabilities
- File system access
- Desktop notifications
- Global keyboard shortcuts
- Portable mode (no installation)

#### Installation Methods (Future)
1. **MSI Installer**: Traditional Windows installer with Start Menu integration
2. **Portable EXE**: Single file, no installation required
3. **Microsoft Store**: One-click install from Windows Store
4. **Chocolatey**: `choco install geneva-bible-study`
5. **Winget**: `winget install GenevaB ibleStudy`

---

### Option 3: Simple HTML Desktop Widget (Lightweight)

Create a minimal HTML-based widget for quick verse access.

#### Create the Widget

1. **Create HTML file** (`BibleWidget.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bible Widget</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            width: 350px;
            height: 500px;
            overflow-y: auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }
        
        .header h1 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .date {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .verse-container {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .verse-text {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 15px;
            font-style: italic;
        }
        
        .verse-reference {
            font-size: 14px;
            font-weight: 600;
            text-align: right;
            opacity: 0.9;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        button {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        
        .reading-plan {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .reading-plan h3 {
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .reading-list {
            font-size: 13px;
            opacity: 0.9;
            line-height: 1.8;
        }
        
        .link {
            display: block;
            text-align: center;
            margin-top: 20px;
            padding: 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            text-decoration: none;
            color: white;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .link:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.02);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📖 Bible Verse of the Day</h1>
        <div class="date" id="current-date"></div>
    </div>
    
    <div class="verse-container">
        <div class="verse-text" id="verse-text">Loading verse...</div>
        <div class="verse-reference" id="verse-reference"></div>
    </div>
    
    <div class="actions">
        <button onclick="copyVerse()">📋 Copy</button>
        <button onclick="refreshVerse()">🔄 New Verse</button>
    </div>
    
    <div class="reading-plan">
        <h3>📅 Today's Reading</h3>
        <div class="reading-list" id="reading-list">
            • Genesis 1-3<br>
            • Psalm 1<br>
            • Matthew 1
        </div>
    </div>
    
    <a href="https://YOUR_USERNAME.github.io/YOUR_REPO/" class="link" target="_blank">
        Open Full App →
    </a>
    
    <script>
        // Sample verses for demonstration
        const verses = [
            {
                text: "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                reference: "John 3:16"
            },
            {
                text: "The Lord is my shepherd; I shall not want.",
                reference: "Psalm 23:1"
            },
            {
                text: "I can do all things through Christ which strengtheneth me.",
                reference: "Philippians 4:13"
            },
            {
                text: "Trust in the Lord with all thine heart; and lean not unto thine own understanding.",
                reference: "Proverbs 3:5"
            },
            {
                text: "For I know the thoughts that I think toward you, saith the Lord, thoughts of peace, and not of evil, to give you an expected end.",
                reference: "Jeremiah 29:11"
            },
            {
                text: "But they that wait upon the Lord shall renew their strength; they shall mount up with wings as eagles.",
                reference: "Isaiah 40:31"
            }
        ];
        
        // Display current date
        function updateDate() {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const today = new Date();
            document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);
        }
        
        // Get verse of the day (consistent per day)
        function getVerseOfDay() {
            const today = new Date();
            const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            const verseIndex = dayOfYear % verses.length;
            return verses[verseIndex];
        }
        
        // Display verse
        function displayVerse(verse) {
            document.getElementById('verse-text').textContent = verse.text;
            document.getElementById('verse-reference').textContent = verse.reference;
        }
        
        // Copy verse to clipboard
        function copyVerse() {
            const verseText = document.getElementById('verse-text').textContent;
            const verseRef = document.getElementById('verse-reference').textContent;
            const fullVerse = `"${verseText}" - ${verseRef}`;
            
            navigator.clipboard.writeText(fullVerse).then(() => {
                alert('Verse copied to clipboard!');
            });
        }
        
        // Get random verse
        function refreshVerse() {
            const randomVerse = verses[Math.floor(Math.random() * verses.length)];
            displayVerse(randomVerse);
        }
        
        // Initialize
        updateDate();
        displayVerse(getVerseOfDay());
    </script>
</body>
</html>
```

2. **Save the file** to your desktop or desired location

3. **Create a shortcut** for easy access:
   - Right-click the HTML file
   - Select **Create shortcut**
   - Move shortcut to desktop
   - Right-click shortcut → **Properties**
   - Add to **Target**: `--window-size=350,500 --app=`
   - Click **OK**

4. **Set to Always on Top** (optional):
   - Install [PowerToys](https://docs.microsoft.com/en-us/windows/powertoys/)
   - Enable "Always on Top" feature
   - Use Win + Ctrl + T to pin the widget

---

## 🎨 Widget Customization

### Resize and Position
```css
/* Modify body styles in the HTML */
body {
    width: 400px;   /* Change width */
    height: 600px;  /* Change height */
}
```

### Change Color Scheme
```css
/* Update gradient colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

### Add More Features
You can extend the widget with:
- Reading plan progress tracking
- Bible book quick links
- Search functionality
- Note-taking
- Bookmark favorites

---

## 🔧 Advanced: Electron Desktop App (For Developers)

### Build Process (Future)

1. **Install Dependencies**:
```bash
npm install electron electron-builder --save-dev
```

2. **Create Electron Main Process** (`electron/main.js`):
```javascript
const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow;
let tray;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        icon: path.join(__dirname, 'icons/icon.png')
    });

    mainWindow.loadURL('https://YOUR_USERNAME.github.io/YOUR_REPO/');
    
    // System tray
    tray = new Tray(path.join(__dirname, 'icons/icon.png'));
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Open', click: () => mainWindow.show() },
        { label: 'Quit', click: () => app.quit() }
    ]);
    tray.setContextMenu(contextMenu);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
```

3. **Add Build Script** (`package.json`):
```json
{
  "scripts": {
    "electron:build": "electron-builder"
  },
  "build": {
    "appId": "com.genevabiblestudy.app",
    "productName": "Geneva Bible Study",
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico"
    }
  }
}
```

4. **Build Windows Executable**:
```bash
npm run electron:build
```

---

## 📋 Widget Usage Tips

### Always-on-Top Setup
1. **Using PowerToys** (Free):
   - Install [Microsoft PowerToys](https://github.com/microsoft/PowerToys)
   - Enable "Always on Top" module
   - Focus widget window
   - Press **Win + Ctrl + T**
   - Widget stays on top

2. **Using DeskPins** (Free):
   - Download [DeskPins](https://deskpins.softonic.com/)
   - Click DeskPins icon in system tray
   - Click the pin
   - Click your widget window

### Auto-Start Widget
1. Press **Win + R**
2. Type `shell:startup`
3. Press **Enter**
4. Copy widget shortcut to this folder
5. Widget opens automatically on Windows startup

### Keyboard Shortcuts (PWA)
- **Ctrl + R**: Refresh content
- **Ctrl + W**: Close widget
- **Ctrl + +**: Zoom in
- **Ctrl + -**: Zoom out

---

## 🎯 Widget Best Practices

### Optimal Widget Sizes
- **Compact**: 300x400px (verse only)
- **Standard**: 350x500px (verse + today's reading)
- **Extended**: 400x600px (verse + reading + notes)

### Position Recommendations
- **Top-right corner**: Easy glance, doesn't cover work
- **Bottom-right**: Near system tray
- **Second monitor**: Dedicated devotional display

### Performance Tips
- Keep widget size reasonable (< 600px width)
- Minimize animations
- Use local storage for caching
- Limit API calls

---

## 🐛 Troubleshooting

### Widget Won't Stay on Top
- Install PowerToys or DeskPins
- Some apps override always-on-top (games, full-screen videos)

### Widget Doesn't Load
- Check internet connection (if using web URLs)
- Try refreshing with Ctrl + R
- Clear browser cache

### Widget Too Large/Small
- Modify HTML CSS width/height values
- Or: Hold Ctrl and scroll to zoom

---

## 📚 Additional Resources

### Windows Tools
- [PowerToys](https://github.com/microsoft/PowerToys) - Always on top & more
- [DeskPins](https://efotinis.neocities.org/deskpins/) - Pin windows
- [AutoHotkey](https://www.autohotkey.com/) - Advanced scripting

### Development Resources
- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Builder](https://www.electron.build/)
- [Windows Dev Center](https://developer.microsoft.com/windows/)

---

## 🚀 Future Widget Features

- [ ] Offline-first architecture
- [ ] Reading plan sync
- [ ] Note-taking widget
- [ ] Multiple widget themes
- [ ] Widget settings panel
- [ ] Hotkey customization
- [ ] Multi-monitor support
- [ ] Transparent background option
- [ ] Widget templates marketplace

---

**Enjoy your Windows Bible Study widget!** 🪟📖✨

For support, visit: [GitHub Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)

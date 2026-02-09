# Build & Run Commands

Complete reference for building and running the Evident application across all platforms.

## Web App (React)

### Development
```bash
# Start dev server
npm run dev

# Start with specific port
PORT=3000 npm run dev

# Start with API proxy
REACT_APP_API_URL=http://localhost:5000 npm run dev
```

### Build
```bash
# Create production build
npm run build

# Analyze bundle size
npm run build:analyze

# Build and serve locally
npm run build && npm run serve
```

### Testing
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test FileDropZone.test.tsx

# Run in watch mode
npm test -- --watch
```

## Mobile App (React Native)

### iOS
```bash
# Install dependencies
cd mobile && npm install && cd ..

# Start iOS dev server
npm run mobile:ios

# Build for iOS
npm run mobile:build:ios

# Run on physical device
npm run mobile:run:ios -- --device
```

### Android
```bash
# Start Android dev server
npm run mobile:android

# Build APK
npm run mobile:build:android

# Run on emulator
npm run mobile:run:android
```

### Test
```bash
# Run mobile tests
npm run mobile:test

# With coverage
npm run mobile:test -- --coverage
```

## Mobile Device Testing

### iOS Device Testing (Mac required)

```bash
# List connected iOS devices
instruments -s devices

# Get device UDID
xcrun xcode-select -p

# Install on real device
react-native run-ios --device "Device Name"

# Example: react-native run-ios --device "Jane's iPhone 14"

# Build only (don't install)
cd mobile && xcodebuild -workspace ios/VideoUpload.xcworkspace \
  -scheme VideoUpload -configuration Debug -device id

# View device logs
# Method 1: Xcode
# Window → Devices and Simulators → Select device → View Console

# Method 2: Command line (requires device UDID)
log stream --device-id <DEVICE_UDID> --predicate 'eventMessage contains "VideoUpload"'

# Clear app cache on device
xcrun simctl erase all
```

### Android Device Testing

```bash
# Enable USB debugging on device:
# Settings → Developer Options → USB Debugging (enable)

# List connected Android devices
adb devices

# Connect to device
adb connect <device-ip>:5555

# Install on real device
react-native run-android

# Install specific APK
adb install app-debug.apk

# Uninstall app
adb uninstall com.evident.videoupload

# View device logs in real-time
adb logcat | grep "VideoUpload\|ReactNative"

# Clear logs
adb logcat -c

# Save logs to file
adb logcat > device-logs.txt &

# Get device info
adb shell getprop ro.build.version.release    # Android version
adb shell getprop ro.product.model             # Device model

# Forward port for development
adb reverse tcp:5000 tcp:5000

# Reboot device
adb reboot
```

### Pre-Device Testing Checklist

```bash
# 1. Install all dependencies
cd mobile && npm install && cd ..

# 2. Run tests first
npm run mobile:test -- --coverage

# 3. Check type errors
npm run type-check

# 4. Lint code
npm run lint

# 5. Build successfully for device
npm run mobile:build:ios    # for iOS
npm run mobile:build:android  # for Android

# 6. Verify backend is running
curl http://localhost:5000/health  # Should return 200 OK

# 7. Verify WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:5000/socket.io/?transport=websocket
```

### Testing Common Scenarios

```bash
# Test with custom API URL
REACT_APP_API_URL=http://192.168.1.100:5000 react-native run-ios

# Test with different backend port
REACT_APP_API_URL=http://localhost:8000 react-native run-android

# Test specific feature (mobile)
# Edit mobile/App.tsx temporarily to test specific screens

# Reset app state for testing
# On device: Settings → Apps → Evident → Clear Cache
# Or: adb shell pm clear com.evident.videoupload
```

### Device Test Validation

```bash
# Capture device screenshots for testing
# iOS: Connect to Xcode, take screenshot in Xcode
xcrun simctl io booted recordVideo output.mp4  # Simulator

# Android: Take screenshot
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# Record device video for bug reporting
# iOS: Built-in screen recording (swipe down from top-right)
# Android: Settings → Developer Options → Enable "Show touches"
```

## Desktop App (Electron)

### Development
```bash
# Start Electron dev environment
npm run electron:dev

# Auto-reload on code changes
npm run electron:dev:watch
```

### Build
```bash
# Build for current platform
npm run electron:build

# Build for all platforms
npm run electron:build:all

# Build for specific platform
npm run electron:build:win      # Windows
npm run electron:build:mac      # macOS
npm run electron:build:linux    # Linux
```

### Package
```bash
# Create installer
npm run electron:pack

# Create installers for all platforms
npm run electron:pack:all
```

## Backend (Python/Flask)

### Development
```bash
# Install dependencies
pip install -r _backend/requirements-dev.txt

# Start development server
python _backend/app.py

# With debug mode
FLASK_ENV=development FLASK_DEBUG=1 python _backend/app.py

# With hot reload
flask --app _backend/app.py run --reload
```

### Run Async Tasks (Celery)
```bash
# Start Celery worker
celery -A _backend.app.celery worker --loglevel=info

# Start with multiple workers
celery -A _backend.app.celery worker --concurrency=4 --loglevel=info

# Monitor tasks
celery -A _backend.app.celery events

# Purge task queue
celery -A _backend.app.celery purge
```

### Database
```bash
# Run migrations
cd _backend && flask db upgrade && cd ..

# Create migration
cd _backend && flask db migrate -m "Description" && cd ..

# Downgrade
cd _backend && flask db downgrade && cd ..
```

## Docker

### Build Images
```bash
# Build backend
docker build -f Dockerfile.backend -t evident-backend:latest .

# Build frontend
docker build -f Dockerfile.frontend -t evident-frontend:latest .

# Build all with compose
docker-compose build
```

### Run Containers
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# View logs
docker-compose logs -f [service]

# Stop all
docker-compose down

# Clean up volumes
docker-compose down -v
```

## Linting & Code Quality

### Format Code
```bash
# Format all files
npm run format

# Format specific directory
npm run format -- components/

# Check formatting (no changes)
npm run format:check
```

### Lint
```bash
# Run ESLint
npm run lint

# Fix ESLint issues
npm run lint:fix

# Run TypeScript check
npm run type-check

# Run SonarQube analysis
npm run sonarqube
```

### Pre-commit
```bash
# Install pre-commit hooks
npx husky install

# Lint-staged runs automatically on commit
# (Configured in lint-staged.config.cjs)
```

## Continuous Integration

### GitHub Actions
```bash
# View workflow status
# Visit: https://github.com/your-repo/actions

# Trigger workflow manually in GitHub UI
# Or via CLI:
gh workflow run tests.yml
```

### Local CI Simulation
```bash
# Run all CI checks locally
npm run ci

# This typically runs:
# - Linting
# - Type checking
# - Tests with coverage
# - Build
```

## Deployment

### Staging
```bash
# Build for staging
npm run build:staging

# Deploy to staging
npm run deploy:staging
```

### Production
```bash
# Build for production
npm run build:production

# Deploy to production
npm run deploy:production

# Verify deployment
npm run verify:production
```

### Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/

# Scale deployment
kubectl scale deployment/evident-web --replicas=3

# View logs
kubectl logs -f deployment/evident-web
```

## Useful Commands

### Clean & Reset
```bash
# Remove all dependencies
npm run clean

# Remove node_modules
rm -rf node_modules && npm install

# Hard reset (safe for development only)
git clean -fd
git reset --hard
```

### Performance
```bash
# Measure build time
npm run build -- --time

# Check bundle size
npm run analyze

# Lighthouse audit
npm run audit:lighthouse
```

### Documentation
```bash
# Generate API docs
npm run docs:generate

# Serve docs locally
npm run docs:serve
```

## Environment Variables

All commands respect `.env.local` and environment-specific files:

- `.env` - Shared defaults
- `.env.development` - Development overrides
- `.env.production` - Production overrides
- `.env.local` - Personal overrides (never commit)

Example:
```bash
# Set for single command
REACT_APP_API_URL=https://api.prod npm run build

# Set for session
export REACT_APP_API_URL=https://api.prod
npm run build
npm run tests
```

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 3000
lsof -i :3000

# Kill it
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

### Module Not Found
```bash
# Clean install
rm -rf node_modules
npm install

# Clear npm cache
npm cache clean --force
```

### CORS Issues
```bash
# Ensure REACT_APP_API_URL matches backend
REACT_APP_API_URL=http://localhost:5000 npm run dev

# Check backend CORS settings
# See _backend/app.py
```

### WebSocket Connection Failed
```bash
# Verify backend is running
curl http://localhost:5000/health

# Check WebSocket endpoint
# Default: http://localhost:5000 (Socket.IO on Flask)
```

For more help, see [README.md](./README.md) and component docs in [components/VideoUpload/README.md](./components/VideoUpload/README.md).

# 🎭 Playwright Navigation Tests

**Comprehensive testing suite for desktop and mobile navigation links**

## 📋 What's Tested

### Desktop Navigation
- ✅ All main nav links (Services, Our Work, Blog, Reviews, Tools)
- ✅ Guides dropdown (8 links)
- ✅ About dropdown (4 links)
- ✅ Dropdown hover behavior
- ✅ Link navigation
- ✅ ARIA attributes
- ✅ Keyboard accessibility

### Mobile Navigation
- ✅ Hamburger menu visibility
- ✅ Mobile nav drawer open/close
- ✅ All mobile nav links
- ✅ Accordion menus (GUIDES, ABOUT)
- ✅ Drawer animations
- ✅ Close on outside click
- ✅ GET ESTIMATE button
- ✅ X button functionality

### Accessibility
- ✅ ARIA labels
- ✅ aria-expanded states
- ✅ aria-haspopup attributes
- ✅ Keyboard navigation
- ✅ Focus states

### Responsive
- ✅ Desktop → Mobile breakpoint (768px)
- ✅ Multiple device sizes
- ✅ iPhone 16 Pro Max
- ✅ iPhone 14
- ✅ Android devices
- ✅ iPad

---

## 🚀 Quick Start

### Install Playwright (First Time)
```bash
npm install -D @playwright/test
npx playwright install
```

### Run All Tests
```bash
npm run test:nav
```

### Run with Browser Visible
```bash
npm run test:nav:headed
```

### Debug Mode (Step Through)
```bash
npm run test:nav:debug
```

### Test Mobile Only
```bash
npm run test:nav:mobile
```

---

## 🎯 PowerShell Scripts

### Test Production Site
```powershell
.\scripts\test-nav-playwright.ps1
```

### Test Local Development
```powershell
.\scripts\test-nav-playwright.ps1 -Environment local
```

### Test Specific Browser
```powershell
# Chrome only
.\scripts\test-nav-playwright.ps1 -Browser chrome

# Firefox only
.\scripts\test-nav-playwright.ps1 -Browser firefox

# Mobile only
.\scripts\test-nav-playwright.ps1 -Browser mobile
```

### Debug Mode
```powershell
.\scripts\test-nav-playwright.ps1 -Debug -Headed
```

---

## 📱 Tested Devices

### Desktop Browsers
- **Chrome** (1920x1080)
- **Firefox** (1920x1080)
- **Safari** (1920x1080)

### Mobile Devices
- **iPhone 16 Pro Max** (430x932)
- **iPhone 14** (390x844)
- **Google Pixel 7** (412x915)
- **iPad Pro** (1024x1366)

---

## 🧪 Test Scenarios

### Desktop Nav Test
1. Load homepage
2. Verify desktop nav visible
3. Verify mobile toggle hidden
4. Check all main links
5. Hover Guides dropdown
6. Verify 8 dropdown links
7. Hover About dropdown
8. Verify 4 dropdown links
9. Click Services link
10. Verify navigation

### Mobile Nav Test
1. Load homepage (mobile viewport)
2. Verify hamburger visible
3. Verify desktop nav hidden
4. Click hamburger
5. Verify drawer opens (aria-hidden=false)
6. Check all nav links visible
7. Click GUIDES accordion
8. Verify submenu expands
9. Check all submenu links
10. Click X button
11. Verify drawer closes
12. Test outside click close

### Accessibility Test
1. Check aria-label on nav
2. Verify aria-expanded states
3. Test aria-haspopup
4. Tab through links
5. Verify keyboard navigation
6. Check focus states

---

## 📊 View Results

### HTML Report (Interactive)
```bash
npx playwright show-report
```

### JSON Results
```bash
cat playwright-report/results.json
```

### Screenshots & Videos
```
test-results/
  ├── screenshots/
  └── videos/
```

---

## ✅ Expected Results

### All Tests Passing
```
✅ Desktop Navigation Tests (10 tests)
✅ Mobile Navigation - iPhone 16 Pro Max (12 tests)
✅ Mobile Navigation - Other Devices (2 tests)
✅ Accessibility Tests (6 tests)
✅ Responsive Breakpoint Tests (1 test)
✅ Header Tests (2 tests)

Total: 33 tests across 7 device configurations
```

---

## 🐛 Debugging Failed Tests

### Run Single Test
```bash
npx playwright test tests/navigation.spec.js -g "should open mobile nav"
```

### Debug Mode
```bash
npx playwright test tests/navigation.spec.js --debug
```

### Headed Mode (See Browser)
```bash
npx playwright test tests/navigation.spec.js --headed
```

### Specific Device
```bash
npx playwright test --project=mobile-chrome-iphone-16-pro-max
```

---

## 📁 File Structure

```
tillerstead.com/
├── tests/
│   └── navigation.spec.js       ← Main test file
├── scripts/
│   └── test-nav-playwright.ps1  ← PowerShell runner
├── playwright.config.js         ← Configuration
├── playwright-report/           ← Test results
└── test-results/                ← Screenshots/videos
```

---

## 🔧 Configuration

### Change Base URL
```javascript
// playwright.config.js
use: {
  baseURL: 'https://tillerstead.com'  // Production
  // OR
  baseURL: 'http://localhost:4000'    // Local
}
```

### Add New Device
```javascript
// playwright.config.js
projects: [
  {
    name: 'mobile-samsung-s23',
    use: {
      ...devices['Galaxy S23'],
      viewport: { width: 360, height: 800 }
    }
  }
]
```

---

## 🎯 Continuous Integration

### GitHub Actions Example
```yaml
name: Navigation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx playwright install --with-deps
      - run: npm run test:nav
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 📈 Performance

- **Average test time:** ~2 minutes (all devices)
- **Single device:** ~20 seconds
- **Desktop only:** ~30 seconds
- **Mobile only:** ~45 seconds

---

## 🚨 Common Issues

### Issue: Tests timeout
**Fix:** Increase timeout in playwright.config.js
```javascript
timeout: 60 * 1000
```

### Issue: Local server not starting
**Fix:** Make sure Jekyll is running
```bash
bundle exec jekyll serve
```

### Issue: Browser not found
**Fix:** Install browsers
```bash
npx playwright install
```

---

## 📞 Support

**Test failures?**
1. Check screenshots in `test-results/`
2. View HTML report: `npx playwright show-report`
3. Run in debug mode: `npm run test:nav:debug`
4. Check browser console for errors

---

**All tests configured and ready to run!** 🎉

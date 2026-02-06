````markdown
# Evident Mobile App Icons

## Required Icons

Place the following icon files in this directory. Icons should be SVG format for best cross-platform scaling.

### Navigation Icons (TabBar)

- `home.png` or `home.svg` - Dashboard/Home
- `folder.png` or `folder.svg` - Cases
- `chart.png` or `chart.svg` - Analysis
- `upload.png` or `upload.svg` - Upload
- `person.png` or `person.svg` - Profile

### Flyout Menu Icons

- `book.png` or `book.svg` - Legal Library
- `document.png` or `document.svg` - Documents
- `settings.png` or `settings.svg` - Settings
- `help.png` or `help.svg` - Help & Support
- `logout.png` or `logout.svg` - Logout

### Detail Page Icons

- `video.png` or `video.svg` - Video content
- `chevron_right.png` or `chevron_right.svg` - Navigation arrows

### App Branding

- `Evident_logo.png` - Main app logo (200x200 minimum)
- `case_placeholder.png` - Placeholder for cases without thumbnails
- `default_avatar.png` - Default user profile image

## Icon Specifications

### Size Requirements

- **SVG**: Preferred for all icons (scalable)
- **PNG**: If using PNG, provide @1x, @2x, @3x versions
  - @1x: 24x24px
  - @2x: 48x48px
  - @3x: 72x72px

### Color Guidelines

- Use monochrome icons for navigation (will be tinted by theme)
- Logo should include brand colors
- Follow Material Design icon guidelines

## Icon Sources

You can obtain icons from:

- [Material Icons](https://fonts.google.com/icons)
- [Ionicons](https://ionic.io/ionicons)
- [Feather Icons](https://feathericons.com/)
- Custom design matching Evident brand

## Adding Icons to Project

1. Place icon files in this directory
2. Icons are automatically included via `Evident.Mobile.csproj`:
   ```xml
   <MauiImage Include="Resources\Images\*" />
   ```
3. Reference in XAML:
   ```xml
   <Image Source="icon_name.png" />
   ```
4. No file extension needed in XAML - MAUI finds the appropriate resource

## Platform-Specific Icons

### iOS

- App icon configured in `Resources/AppIcon/appicon.svg`
- Launch screen in `Resources/Splash/splash.svg`

### Android

- App icon configured in `Resources/AppIcon/appicon.svg`
- Adaptive icon foreground in `Resources/AppIcon/appiconfg.svg`

### Windows

- App icon configured in `Resources/AppIcon/appicon.svg`
- Tile images generated automatically

````

#!/usr/bin/env python3
"""
Generate all necessary icons and social share images from logo
Creates favicons, Apple touch icons, PWA icons, and Open Graph images
"""

from PIL import Image, ImageDraw, ImageFilter
import os
from pathlib import Path

# Configuration
SOURCE_LOGO = "assets/img/logo/logo-optimized.png"  # Best available logo
OUTPUT_DIR = Path("assets/icons")
SOCIAL_DIR = Path("assets/img/social")

# Icon sizes needed
ICON_SIZES = {
    # Favicons
    'favicon-16x16.png': 16,
    'favicon-32x32.png': 32,
    'favicon-48x48.png': 48,
    
    # Apple Touch Icons
    'apple-touch-icon.png': 180,  # Default
    'apple-touch-icon-180x180.png': 180,
    'apple-touch-icon-152x152.png': 152,
    'apple-touch-icon-120x120.png': 120,
    'apple-touch-icon-76x76.png': 76,
    'apple-touch-icon-60x60.png': 60,
    'apple-touch-icon-precomposed.png': 180,
    
    # Android/Chrome PWA
    'android-chrome-192x192.png': 192,
    'android-chrome-512x512.png': 512,
    
    # Microsoft
    'mstile-70x70.png': 70,
    'mstile-144x144.png': 144,
    'mstile-150x150.png': 150,
    'mstile-310x150.png': (310, 150),  # Wide tile
    'mstile-310x310.png': 310,
}

# Social share image sizes
SOCIAL_SIZES = {
    # Open Graph (Facebook, LinkedIn)
    'og-image.png': (1200, 630),
    'og-image-square.png': (1200, 1200),
    
    # Twitter Cards
    'twitter-card.png': (1200, 675),
    'twitter-card-summary.png': (800, 800),
    
    # Generic social
    'social-share.png': (1200, 630),
    'social-share-square.png': (600, 600),
}

def create_rounded_icon(image, size, radius_percent=0.2):
    """Create icon with rounded corners"""
    if isinstance(size, tuple):
        width, height = size
    else:
        width = height = size
    
    # Resize image
    img = image.copy()
    img.thumbnail((width, height), Image.Resampling.LANCZOS)
    
    # Create new image with transparency
    output = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Calculate position to center the logo
    paste_x = (width - img.width) // 2
    paste_y = (height - img.height) // 2
    
    # Paste logo centered
    output.paste(img, (paste_x, paste_y), img if img.mode == 'RGBA' else None)
    
    # Create rounded mask
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    radius = int(min(width, height) * radius_percent)
    draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
    
    # Apply mask
    output.putalpha(mask)
    
    return output

def create_social_image(logo, size, bg_color='#10b981'):
    """Create social share image with logo centered on brand background"""
    width, height = size
    
    # Create background
    background = Image.new('RGB', (width, height), bg_color)
    
    # Calculate logo size (60% of smaller dimension)
    logo_size = int(min(width, height) * 0.6)
    
    # Resize logo
    logo_copy = logo.copy()
    logo_copy.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Calculate center position
    x = (width - logo_copy.width) // 2
    y = (height - logo_copy.height) // 2
    
    # Paste logo on background
    if logo_copy.mode == 'RGBA':
        background.paste(logo_copy, (x, y), logo_copy)
    else:
        background.paste(logo_copy, (x, y))
    
    return background

def main():
    """Generate all icons and social images"""
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SOCIAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if source logo exists
    if not Path(SOURCE_LOGO).exists():
        print(f"❌ Source logo not found: {SOURCE_LOGO}")
        print("Looking for alternative logo files...")
        
        # Try alternatives
        alternatives = [
            "assets/img/logo/logo-optimized@2x.png",
            "assets/img/logo/tillerstead_social_circle_1024.png",
            "assets/img/logo/logo-header@2x.png",
        ]
        
        source = None
        for alt in alternatives:
            if Path(alt).exists():
                source = alt
                print(f"✓ Found: {alt}")
                break
        
        if not source:
            print("❌ No suitable logo file found!")
            return
    else:
        source = SOURCE_LOGO
    
    # Load source logo
    print(f"\n📸 Loading source logo: {source}")
    logo = Image.open(source)
    
    # Convert to RGBA if needed
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')
    
    print(f"✓ Logo loaded: {logo.size[0]}x{logo.size[1]} px\n")
    
    # Generate icons
    print("🎨 Generating icons...")
    for filename, size in ICON_SIZES.items():
        output_path = OUTPUT_DIR / filename
        
        if isinstance(size, tuple):
            # Wide tile special handling
            icon = create_rounded_icon(logo, size, radius_percent=0.1)
        else:
            # Square icons with rounded corners
            icon = create_rounded_icon(logo, size)
        
        icon.save(output_path, 'PNG', optimize=True)
        print(f"  ✓ {filename}")
    
    # Generate favicon.ico (multi-resolution)
    print("\n🔖 Generating favicon.ico...")
    favicon_sizes = [(16, 16), (32, 32), (48, 48)]
    icons = []
    for size in favicon_sizes:
        icon = create_rounded_icon(logo, size[0])
        icons.append(icon)
    
    icons[0].save(
        'favicon.ico',
        format='ICO',
        sizes=favicon_sizes,
        append_images=icons[1:]
    )
    print("  ✓ favicon.ico")
    
    # Generate social share images
    print("\n🌐 Generating social share images...")
    for filename, size in SOCIAL_SIZES.items():
        output_path = SOCIAL_DIR / filename
        social_img = create_social_image(logo, size)
        social_img.save(output_path, 'PNG', optimize=True, quality=95)
        print(f"  ✓ {filename}")
    
    # Also create WebP versions for modern browsers
    print("\n⚡ Creating WebP versions...")
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith('.png'):
            png_path = OUTPUT_DIR / filename
            webp_path = OUTPUT_DIR / filename.replace('.png', '.webp')
            img = Image.open(png_path)
            img.save(webp_path, 'WEBP', quality=90, method=6)
            print(f"  ✓ {filename.replace('.png', '.webp')}")
    
    for filename in os.listdir(SOCIAL_DIR):
        if filename.endswith('.png'):
            png_path = SOCIAL_DIR / filename
            webp_path = SOCIAL_DIR / filename.replace('.png', '.webp')
            img = Image.open(png_path)
            img.save(webp_path, 'WEBP', quality=92, method=6)
            print(f"  ✓ {filename.replace('.png', '.webp')}")
    
    print("\n✅ All icons and social images generated successfully!")
    print(f"\n📁 Icons saved to: {OUTPUT_DIR}")
    print(f"📁 Social images saved to: {SOCIAL_DIR}")
    print("\n💡 Next steps:")
    print("   1. Update manifest.webmanifest with new icon paths")
    print("   2. Update browserconfig.xml for Microsoft tiles")
    print("   3. Update meta tags in _includes/icons/favicon-meta.html")
    print("   4. Update Open Graph tags for social share images")

if __name__ == '__main__':
    main()

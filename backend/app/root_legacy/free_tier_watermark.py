"""
FREE Tier Watermark Service
Adds watermarks to exports for FREE tier users
Encourages upgrades while providing value
"""

import io

from .models_auth import TierLevel

# Optional imports for watermarking
try:
    from pypdf import PdfReader, PdfWriter  # Migrated from PyPDF2 (deprecated)
    from reportlab.lib.colors import Color
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class WatermarkService:
    """Handles watermarking for FREE tier exports"""

    # Watermark text for different export types
    WATERMARK_TEXTS = {
        "pdf": "Evident FREE Trial - Upgrade at Evident.info/pricing",
        "video": "Evident FREE Trial",
        "image": "Evident FREE Trial",
        "report": "Generated with Evident FREE Tier - Upgrade for watermark-free exports",
    }

    @staticmethod
    def should_watermark(user):
        """
        Check if user's exports should be watermarked

        Args:
            user: User object

        Returns:
            bool: True if watermark required
        """
        return user.tier == TierLevel.FREE

    @staticmethod
    def add_pdf_watermark(input_pdf_path, output_pdf_path, user):
        """
        Add watermark to PDF document

        Args:
            input_pdf_path: Path to input PDF
            output_pdf_path: Path to save watermarked PDF
            user: User object

        Returns:
            bool: Success
        """
        if not REPORTLAB_AVAILABLE:
            print("Warning: reportlab not installed, skipping watermark")
            import shutil

            shutil.copy(input_pdf_path, output_pdf_path)
            return True

        if not WatermarkService.should_watermark(user):
            # No watermark needed, just copy
            import shutil

            shutil.copy(input_pdf_path, output_pdf_path)
            return True

        try:
            # Create watermark PDF
            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer, pagesize=letter)

            # Set watermark style
            c.setFont("Helvetica", 10)
            c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.5))  # Light gray, semi-transparent

            # Add watermark text (centered at bottom)
            watermark_text = WatermarkService.WATERMARK_TEXTS["pdf"]
            text_width = c.stringWidth(watermark_text, "Helvetica", 10)
            x = (letter[0] - text_width) / 2
            y = 20  # 20 points from bottom

            c.drawString(x, y, watermark_text)
            c.save()

            # Read original PDF
            watermark_buffer.seek(0)
            watermark_pdf = PdfReader(watermark_buffer)
            watermark_page = watermark_pdf.pages[0]

            input_pdf = PdfReader(input_pdf_path)
            output_pdf = PdfWriter()

            # Add watermark to each page
            for page in input_pdf.pages:
                page.merge_page(watermark_page)
                output_pdf.add_page(page)

            # Write output
            with open(output_pdf_path, "wb") as f:
                output_pdf.write(f)

            return True

        except Exception as e:
            print(f"Error adding PDF watermark: {e}")
            return False

    @staticmethod
    def add_image_watermark(image_path, output_path, user):
        """
        Add watermark to image (screenshots, exports, etc.)

        Args:
            image_path: Path to input image
            output_path: Path to save watermarked image
            user: User object

        Returns:
            bool: Success
        """
        if not PIL_AVAILABLE:
            print("Warning: PIL not installed, skipping watermark")
            import shutil

            shutil.copy(image_path, output_path)
            return True

        if not WatermarkService.should_watermark(user):
            import shutil

            shutil.copy(image_path, output_path)
            return True

        try:
            # Open image
            img = Image.open(image_path)

            # Create drawing context
            draw = ImageDraw.Draw(img)

            # Get image size
            width, height = img.size

            # Load font (try to use a nice font, fallback to default)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()

            # Watermark text
            watermark_text = WatermarkService.WATERMARK_TEXTS["image"]

            # Calculate text size and position (bottom right)
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = width - text_width - 20
            y = height - text_height - 20

            # Draw semi-transparent background
            padding = 10
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(255, 255, 255, 180),
            )

            # Draw text
            draw.text((x, y), watermark_text, fill=(100, 100, 100), font=font)

            # Save
            img.save(output_path)
            return True

        except Exception as e:
            print(f"Error adding image watermark: {e}")
            return False

    @staticmethod
    def add_html_watermark(html_content, user):
        """
        Add watermark banner to HTML reports

        Args:
            html_content: HTML string
            user: User object

        Returns:
            str: HTML with watermark (or original if no watermark needed)
        """
        if not WatermarkService.should_watermark(user):
            return html_content

        watermark_banner = f"""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(90deg, rgba(255,193,7,0.95) 0%, rgba(255,152,0,0.95) 100%);
            color: #333;
            padding: 12px 20px;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 9999;
        ">
            <span style="margin-right: 15px;">
                🎯 {WatermarkService.WATERMARK_TEXTS['report']}
            </span>
            <a href="https://Evident.info/pricing" style="
                background: white;
                color: #ff6f00;
                padding: 6px 16px;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
                transition: all 0.2s;
            ">
                Upgrade Now →
            </a>
        </div>
        <div style="height: 60px;"></div> <!-- Spacer to prevent content overlap -->
        """

        # Insert before closing body tag
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{watermark_banner}</body>")
        else:
            html_content += watermark_banner

        return html_content

    @staticmethod
    def get_watermark_notice(export_type="general"):
        """
        Get watermark notice for UI display

        Args:
            export_type: 'pdf', 'video', 'image', 'report', 'general'

        Returns:
            dict: Notice information
        """
        return {
            "watermarked": True,
            "tier": "FREE",
            "message": f"FREE tier exports include a watermark. Upgrade to remove.",
            "watermark_text": WatermarkService.WATERMARK_TEXTS.get(
                export_type, WatermarkService.WATERMARK_TEXTS["pdf"]
            ),
            "upgrade_cta": {
                "text": "Remove Watermarks - Upgrade to STARTER",
                "url": "/pricing",
                "price": "$29/month",
            },
        }


def watermark_decorator(export_type="pdf"):
    """
    Decorator for export functions to automatically handle watermarking

    Usage:
        @watermark_decorator(export_type='pdf')
        def export_report(user, content):
            # Your export logic
            return file_path
    """
    from functools import wraps

    from flask_login import current_user

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the file path from the original function
            result = f(*args, **kwargs)

            # If FREE tier, add watermark
            if hasattr(current_user, "tier") and current_user.tier == TierLevel.FREE:
                if export_type == "pdf" and isinstance(result, str):
                    # Watermark PDF in place
                    temp_path = result + ".temp"
                    WatermarkService.add_pdf_watermark(result, temp_path, current_user)
                    import os

                    os.replace(temp_path, result)

                elif export_type == "html" and isinstance(result, str):
                    # Add HTML banner
                    result = WatermarkService.add_html_watermark(result, current_user)

            return result

        return decorated_function

    return decorator


# Export key components
__all__ = ["WatermarkService", "watermark_decorator"]



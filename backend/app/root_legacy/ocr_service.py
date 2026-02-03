"""
OCR Service for Scanned Documents
Extracts text from images, scanned PDFs, and handwritten documents
"""

import hashlib
import io
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PIL import Image


class OCRService:
    """
    Professional OCR service for legal documents

    Features:
    - Text extraction from images and scanned PDFs
    - Handwriting recognition
    - Form field extraction
    - Layout preservation
    - Multi-language support
    - Batch processing
    """

    def __init__(self, engine: str = "tesseract"):
        """
        Initialize OCR service

        Args:
            engine: 'tesseract' (free, local) or 'aws' (AWS Textract, paid)
        """
        self.engine = engine
        self.tesseract = None
        self.textract_client = None
        self.supported_image_formats = [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]

    def _load_tesseract(self):
        """Lazy load Tesseract OCR"""
        if self.tesseract is None and self.engine == "tesseract":
            try:
                import pytesseract

                self.tesseract = pytesseract
                print("✓ Tesseract OCR loaded")
            except ImportError:
                raise ImportError(
                    "Tesseract not installed. Run: pip install pytesseract\n"
                    "Also install Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki"
                )

    def _load_textract(self):
        """Lazy load AWS Textract"""
        if self.textract_client is None and self.engine == "aws":
            try:
                import boto3

                self.textract_client = boto3.client("textract")
                print("✓ AWS Textract client loaded")
            except ImportError:
                raise ImportError("AWS SDK not installed. Run: pip install boto3")

    def extract_text_from_image(
        self, image_path: str, language: str = "eng", preserve_layout: bool = False
    ) -> Dict:
        """
        Extract text from image file

        Args:
            image_path: Path to image file
            language: OCR language code (eng, spa, fra, etc.)
            preserve_layout: Maintain original document layout

        Returns:
            {
                'text': 'Extracted text...',
                'confidence': 0.92,
                'language': 'eng',
                'words': [...],
                'blocks': [...],
                'metadata': {...}
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in self.supported_image_formats:
            raise ValueError(
                f"Unsupported format: {file_ext}. "
                f"Supported: {', '.join(self.supported_image_formats)}"
            )

        if self.engine == "tesseract":
            return self._extract_with_tesseract(image_path, language, preserve_layout)
        elif self.engine == "aws":
            return self._extract_with_textract(image_path)
        else:
            raise ValueError(f"Unknown OCR engine: {self.engine}")

    def _extract_with_tesseract(
        self, image_path: str, language: str, preserve_layout: bool
    ) -> Dict:
        """Extract text using Tesseract OCR"""
        self._load_tesseract()

        # Open image
        img = Image.open(image_path)

        # Get detailed data
        data = self.tesseract.image_to_data(
            img, lang=language, output_type=self.tesseract.Output.DICT
        )

        # Extract full text
        if preserve_layout:
            text = self.tesseract.image_to_string(img, lang=language)
        else:
            text = " ".join([word for word in data["text"] if word.strip()])

        # Calculate confidence
        confidences = [int(conf) for conf in data["conf"] if conf != "-1" and str(conf).isdigit()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Extract words with bounding boxes
        words = []
        for i in range(len(data["text"])):
            if data["text"][i].strip():
                words.append(
                    {
                        "text": data["text"][i],
                        "confidence": int(data["conf"][i]) / 100 if data["conf"][i] != "-1" else 0,
                        "bbox": {
                            "left": data["left"][i],
                            "top": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                        },
                    }
                )

        # Group into blocks (paragraphs)
        blocks = self._group_into_blocks(data)

        return {
            "text": text.strip(),
            "confidence": round(avg_confidence / 100, 2),
            "language": language,
            "words": words,
            "blocks": blocks,
            "metadata": {
                "file_path": image_path,
                "file_name": os.path.basename(image_path),
                "file_size": os.path.getsize(image_path),
                "engine": "tesseract",
                "image_size": img.size,
                "ocr_date": datetime.now().isoformat(),
                "checksum": self._calculate_checksum(image_path),
            },
        }

    def _extract_with_textract(self, image_path: str) -> Dict:
        """Extract text using AWS Textract (premium, more accurate)"""
        self._load_textract()

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Call Textract
        response = self.textract_client.detect_document_text(Document={"Bytes": image_bytes})

        # Extract text and confidence
        text_lines = []
        words = []
        avg_confidence = 0
        conf_count = 0

        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                text_lines.append(block["Text"])
                avg_confidence += block["Confidence"]
                conf_count += 1
            elif block["BlockType"] == "WORD":
                words.append(
                    {
                        "text": block["Text"],
                        "confidence": block["Confidence"] / 100,
                        "bbox": block["Geometry"]["BoundingBox"],
                    }
                )

        text = "\n".join(text_lines)
        confidence = (avg_confidence / conf_count / 100) if conf_count > 0 else 0

        return {
            "text": text,
            "confidence": round(confidence, 2),
            "language": "auto",
            "words": words,
            "blocks": response["Blocks"],
            "metadata": {
                "file_path": image_path,
                "file_name": os.path.basename(image_path),
                "file_size": os.path.getsize(image_path),
                "engine": "aws-textract",
                "ocr_date": datetime.now().isoformat(),
                "checksum": self._calculate_checksum(image_path),
            },
        }

    def extract_text_from_pdf(self, pdf_path: str, language: str = "eng") -> Dict:
        """
        Extract text from scanned PDF

        Handles multi-page PDFs by OCR'ing each page
        """
        try:
            import pdf2image
        except ImportError:
            raise ImportError(
                "pdf2image not installed. Run: pip install pdf2image\n"
                "Also install poppler: https://github.com/oschwartz10612/poppler-windows/releases/"
            )

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Convert PDF pages to images
        print(f"Converting PDF to images: {os.path.basename(pdf_path)}")
        images = pdf2image.convert_from_path(pdf_path)

        # OCR each page
        all_text = []
        all_words = []
        all_confidences = []

        for i, img in enumerate(images, 1):
            print(f"  Page {i}/{len(images)}...")

            # Save temp image
            temp_path = f"temp_page_{i}.png"
            img.save(temp_path)

            # OCR
            result = self.extract_text_from_image(temp_path, language)
            all_text.append(f"--- Page {i} ---\n{result['text']}")
            all_words.extend(result["words"])
            all_confidences.append(result["confidence"])

            # Cleanup
            os.remove(temp_path)

        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0

        return {
            "text": "\n\n".join(all_text),
            "confidence": round(avg_confidence, 2),
            "language": language,
            "pages": len(images),
            "words": all_words,
            "metadata": {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "file_size": os.path.getsize(pdf_path),
                "engine": self.engine,
                "page_count": len(images),
                "ocr_date": datetime.now().isoformat(),
                "checksum": self._calculate_checksum(pdf_path),
            },
        }

    def extract_form_fields(self, image_path: str) -> Dict:
        """
        Extract form fields from structured documents
        (checkboxes, signatures, form values)

        Requires AWS Textract (premium feature)
        """
        if self.engine != "aws":
            raise ValueError("Form field extraction requires AWS Textract engine")

        self._load_textract()

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Analyze document
        response = self.textract_client.analyze_document(
            Document={"Bytes": image_bytes}, FeatureTypes=["FORMS", "TABLES"]
        )

        # Extract key-value pairs
        form_fields = {}
        for block in response["Blocks"]:
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block["EntityTypes"]:
                    key = self._get_text_from_relationship(block, response["Blocks"])
                    value = self._get_value_from_relationship(block, response["Blocks"])
                    if key:
                        form_fields[key] = value

        return {
            "form_fields": form_fields,
            "raw_response": response,
            "metadata": {
                "file_path": image_path,
                "engine": "aws-textract-forms",
                "extracted_at": datetime.now().isoformat(),
            },
        }

    def batch_ocr(self, file_paths: List[str], **kwargs) -> List[Dict]:
        """Process multiple files with OCR"""
        results = []

        for i, file_path in enumerate(file_paths, 1):
            print(f"\n[{i}/{len(file_paths)}] Processing: {os.path.basename(file_path)}")

            try:
                # Determine file type
                ext = os.path.splitext(file_path)[1].lower()

                if ext == ".pdf":
                    result = self.extract_text_from_pdf(file_path, **kwargs)
                else:
                    result = self.extract_text_from_image(file_path, **kwargs)

                results.append({"success": True, "file": file_path, "result": result})

                print(f"  ✓ Confidence: {result['confidence']*100:.1f}%")

            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                results.append({"success": False, "file": file_path, "error": str(e)})

        return results

    def _group_into_blocks(self, data: Dict) -> List[Dict]:
        """Group words into text blocks (paragraphs)"""
        blocks = []
        current_block = []
        current_block_num = data["block_num"][0] if data["block_num"] else None

        for i in range(len(data["text"])):
            if data["text"][i].strip():
                block_num = data["block_num"][i]

                if block_num != current_block_num and current_block:
                    blocks.append({"text": " ".join(current_block), "block_id": current_block_num})
                    current_block = []

                current_block.append(data["text"][i])
                current_block_num = block_num

        if current_block:
            blocks.append({"text": " ".join(current_block), "block_id": current_block_num})

        return blocks

    def _get_text_from_relationship(self, block: Dict, all_blocks: List[Dict]) -> str:
        """Helper for form field extraction"""
        text = []
        if "Relationships" in block:
            for relationship in block["Relationships"]:
                if relationship["Type"] == "CHILD":
                    for child_id in relationship["Ids"]:
                        child_block = next((b for b in all_blocks if b["Id"] == child_id), None)
                        if child_block and child_block["BlockType"] == "WORD":
                            text.append(child_block["Text"])
        return " ".join(text)

    def _get_value_from_relationship(self, block: Dict, all_blocks: List[Dict]) -> str:
        """Helper for form field extraction"""
        if "Relationships" in block:
            for relationship in block["Relationships"]:
                if relationship["Type"] == "VALUE":
                    for value_id in relationship["Ids"]:
                        value_block = next((b for b in all_blocks if b["Id"] == value_id), None)
                        if value_block:
                            return self._get_text_from_relationship(value_block, all_blocks)
        return ""

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


# Example usage
if __name__ == "__main__":
    # Initialize OCR service
    ocr = OCRService(engine="tesseract")

    print("OCR Service Examples")
    print("=" * 80)

    # Example 1: Image OCR
    # result = ocr.extract_text_from_image("arrest_report_scan.jpg")
    # print(f"Text: {result['text'][:200]}...")
    # print(f"Confidence: {result['confidence']*100:.1f}%")

    # Example 2: PDF OCR
    # result = ocr.extract_text_from_pdf("scanned_document.pdf")
    # print(f"Pages: {result['pages']}")
    # print(f"Confidence: {result['confidence']*100:.1f}%")

    # Example 3: Batch processing
    # files = ["doc1.jpg", "doc2.pdf", "doc3.png"]
    # results = ocr.batch_ocr(files)

    print("\n✓ OCR Service ready!")
    print("  Tesseract: pip install pytesseract pdf2image")
    print("  AWS: pip install boto3")

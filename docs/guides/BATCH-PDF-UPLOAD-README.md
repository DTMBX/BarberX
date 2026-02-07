# Batch PDF Upload Feature

## Overview

The Batch PDF Upload feature allows users to upload multiple PDF files
simultaneously through a drag-and-drop interface. This is useful for uploading
case documents, legal briefs, motions, and other PDF files in bulk.

## Files Created

### 1. Frontend Pages

- **`batch-pdf-upload.html`** - Main upload interface with drag-and-drop
  functionality
- **`pdf-management.html`** - Admin/management interface to view and manage
  uploaded PDFs

### 2. Backend Updates

- **`app.py`** - Added PDFUpload model and API endpoints:
  - `PDFUpload` database model (lines ~361-426)
  - `/api/upload/pdf` - Single PDF upload endpoint
  - `/api/upload/pdf/batch` - Batch PDF upload endpoint
  - `/api/pdfs` - List uploaded PDFs
  - `/api/pdf/<id>` - Get PDF info
  - `/api/pdf/<id>/download` - Download PDF
  - `/api/pdf/<id>` DELETE - Delete PDF

### 3. Database Migration

- **`migrate_add_pdf_uploads.py`** - Migration script to add pdf_uploads table

## Features

### Upload Interface (`batch-pdf-upload.html`)

- **Drag & Drop** - Drag files directly onto the upload zone
- **Click to Browse** - Traditional file picker
- **Batch Processing** - Upload up to 100 PDFs at once
- **Real-time Progress** - Track upload status for each file
- **Validation** - File type and size validation
- **File Management** - Remove files before upload, clear all

### Management Interface (`pdf-management.html`)

- **Statistics Dashboard** - Total files, size, recent uploads
- **Search & Filter** - Search by filename, filter by status/type
- **File Operations** - Download and delete PDFs
- **Pagination** - Handle large numbers of uploads
- **Responsive Table** - View file details, metadata, tags

## Database Schema

### PDFUpload Model

```sql
CREATE TABLE pdf_uploads (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,  - Foreign key to users table
    filename VARCHAR(255),  - Stored filename
    original_filename VARCHAR(255),  - Original upload name
    file_path VARCHAR(500),  - Path on server
    file_size INTEGER,  - Size in bytes
    file_hash VARCHAR(64),  - SHA-256 hash (unique)
    mime_type VARCHAR(100),  - Default: application/pdf
    case_number VARCHAR(100),  - Optional case reference
    document_type VARCHAR(100),  - brief, motion, order, etc.
    tags JSON,  - Array of tags
    description TEXT,  - Optional description
    status VARCHAR(20),  - uploaded, processing, processed, error
    page_count INTEGER,  - PDF page count
    extracted_text TEXT,  - Extracted text content
    created_at DATETIME,
    processed_at DATETIME,
    is_public BOOLEAN,  - Public access flag
    share_token VARCHAR(64),  - Sharing token
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Installation & Setup

### 1. Run Database Migration

```bash
python migrate_add_pdf_uploads.py
```

This will create the `pdf_uploads` table in your database.

### 2. Create Upload Directory

The upload directory is created automatically, but you can pre-create it:

```bash
mkdir -p uploads/pdfs
```

### 3. Access the Features

#### Upload PDFs

Navigate to: `http://localhost:5000/batch-pdf-upload.html`

#### Manage PDFs

Navigate to: `http://localhost:5000/pdf-management.html`

## API Endpoints

### Upload Single PDF

```http
POST /api/upload/pdf
Content-Type: multipart/form-data

file: <PDF file>
case_number: (optional)
document_type: (optional)
description: (optional)
tags: (optional, comma-separated)
```

Response:

```json
{
  "success": true,
  "upload_id": 1,
  "filename": "document.pdf",
  "file_hash": "abc123...",
  "file_size": 1048576,
  "message": "PDF uploaded successfully"
}
```

### Batch Upload PDFs

```http
POST /api/upload/pdf/batch
Content-Type: multipart/form-data

files: [<PDF file 1>, <PDF file 2>, ...]
```

Response:

```json
{
  "success": true,
  "results": {
    "total": 5,
    "successful": [...],
    "failed": [...]
  },
  "summary": {
    "total": 5,
    "successful": 4,
    "failed": 1
  }
}
```

### List PDFs

```http
GET /api/pdfs?page=1&per_page=50
```

Response:

```json
{
  "total": 100,
  "page": 1,
  "per_page": 50,
  "total_pages": 2,
  "pdfs": [...]
}
```

### Get PDF Info

```http
GET /api/pdf/<id>
```

### Download PDF

```http
GET /api/pdf/<id>/download
```

### Delete PDF

```http
DELETE /api/pdf/<id>
```

(Requires authentication)

## Configuration

### File Size Limits

Default: 50 MB per file Edit in `batch-pdf-upload.html`:

```javascript
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
```

### Max Files

Default: 100 files per batch Edit in `batch-pdf-upload.html`:

```javascript
const MAX_FILES = 100;
```

### Upload Directory

Default: `./uploads/pdfs` Edit in `app.py` if needed:

```python
upload_dir = Path('./uploads/pdfs')
```

## Security Features

1. **File Validation** - Only PDF files accepted
2. **Filename Sanitization** - Secure filenames using `secure_filename()`
3. **Hash Verification** - SHA-256 hash for file integrity
4. **Access Control** - User-based permissions
5. **Audit Logging** - All uploads logged in audit_logs table

## Future Enhancements

- [ ] PDF text extraction on upload
- [ ] PDF thumbnail generation
- [ ] OCR for scanned documents
- [ ] Full-text search across PDFs
- [ ] Metadata extraction (author, date, etc.)
- [ ] Folder/category organization
- [ ] Bulk tagging and categorization
- [ ] Export uploaded files as ZIP

## Troubleshooting

### Upload Fails

- Check file size limits
- Verify file is a valid PDF
- Check server storage space
- Review browser console for errors

### Files Not Showing in Management

- Ensure database migration ran successfully
- Check user permissions
- Verify API endpoint responses

### Database Errors

- Run migration script again
- Check database permissions
- Verify SQLAlchemy configuration

## Support

For issues or questions:

1. Check server logs: `logs/Evident.log`
2. Review browser console
3. Verify database schema
4. Check file permissions on upload directory

--

**Created**: January 23, 2026 **Version**: 1.0 **Author**: Evident Legal
Technologies

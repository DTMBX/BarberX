-- Legal Library Unified Retrieval Schema
-- Evident_legal.db

-- Documents table: all ingested legal documents
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id TEXT UNIQUE NOT NULL,
  sha256 TEXT NOT NULL,
  filename TEXT NOT NULL,
  storage_path_original TEXT NOT NULL,
  source_system TEXT NOT NULL,
  document_type TEXT,
  metadata TEXT,
  indexed_at TEXT DEFAULT (datetime('now')),
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS document_pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  text_content TEXT NOT NULL,
  metadata TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(document_id) REFERENCES documents(document_id),
  UNIQUE(document_id, page_number)
);

CREATE VIRTUAL TABLE IF NOT EXISTS document_fts
USING fts5(
  document_id UNINDEXED,
  page_number UNINDEXED,
  text_content,
  content='document_pages',
  content_rowid='id',
  tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS document_pages_ai AFTER INSERT ON document_pages BEGIN
  INSERT INTO document_fts(rowid, document_id, page_number, text_content)
  VALUES (new.id, new.document_id, new.page_number, new.text_content);
END;

CREATE TRIGGER IF NOT EXISTS document_pages_ad AFTER DELETE ON document_pages BEGIN
  INSERT INTO document_fts(document_fts, rowid, document_id, page_number, text_content)
  VALUES ('delete', old.id, old.document_id, old.page_number, old.text_content);
END;

CREATE TRIGGER IF NOT EXISTS document_pages_au AFTER UPDATE ON document_pages BEGIN
  INSERT INTO document_fts(document_fts, rowid, document_id, page_number, text_content)
  VALUES ('delete', old.id, old.document_id, old.page_number, old.text_content);
  INSERT INTO document_fts(rowid, document_id, page_number, text_content)
  VALUES (new.id, new.document_id, new.page_number, new.text_content);
END;

CREATE TABLE IF NOT EXISTS citations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id TEXT NOT NULL,
  document_id TEXT NOT NULL,
  page_number INTEGER,
  text_start INTEGER,
  text_end INTEGER,
  snippet TEXT NOT NULL,
  citation_rank INTEGER,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(document_id) REFERENCES documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_citations_analysis ON citations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_citations_document ON citations(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source_system);
CREATE INDEX IF NOT EXISTS idx_pages_document ON document_pages(document_id);

CREATE TABLE IF NOT EXISTS muni_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  state TEXT NOT NULL DEFAULT 'NJ',
  county TEXT NOT NULL,
  municipality TEXT NOT NULL,
  provider TEXT,
  base_url TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(state, county, municipality)
);

CREATE TABLE IF NOT EXISTS muni_code_sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  section_citation TEXT NOT NULL,
  section_path TEXT,
  title TEXT,
  text TEXT NOT NULL,
  effective_date TEXT,
  last_updated TEXT,
  retrieved_at TEXT DEFAULT (datetime('now')),
  source_url TEXT,
  sha256 TEXT,
  FOREIGN KEY(source_id) REFERENCES muni_sources(id),
  UNIQUE(source_id, section_citation)
);

CREATE VIRTUAL TABLE IF NOT EXISTS muni_fts
USING fts5(county, municipality, section_citation, title, text, content='');

CREATE INDEX IF NOT EXISTS idx_muni_sections_source ON muni_code_sections(source_id);

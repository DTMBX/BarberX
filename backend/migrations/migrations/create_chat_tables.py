# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database Migration: Enhanced Chat Tables

Creates tables for:
- conversations: Conversation metadata
- messages: Individual messages in conversations
- message_citations: Links messages to cited documents
- conversation_topics: Topic tags for conversations
- conversation_references: Track document references

Run with: python migrations/create_chat_tables.py
"""

import sqlite3
from pathlib import Path


def create_chat_tables(db_path: str = "instance/Evident_legal.db"):
    """Create enhanced chat tables in database"""

    # Ensure instance directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Creating enhanced chat tables in {db_path}...")

    # 1. Conversations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_id INTEGER,
            title TEXT NOT NULL,
            context_documents TEXT,  -- JSON array of doc_ids
            metadata TEXT,  -- JSON for custom metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )
    print("✓ Created conversations table")

    # Index for fast user queries
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversations_user 
        ON conversations(user_id, created_at DESC)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversations_project 
        ON conversations(project_id)
    """
    )

    # 2. Messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant')),
            content TEXT NOT NULL,
            tokens_used INTEGER,
            model TEXT,
            metadata TEXT,  -- JSON for additional metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """
    )
    print("✓ Created messages table")

    # Index for conversation retrieval
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_conversation 
        ON messages(conversation_id, created_at ASC)
    """
    )

    # Full-text search on message content
    cursor.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            message_id UNINDEXED,
            role,
            content,
            tokenize='porter'
        )
    """
    )
    print("✓ Created messages_fts full-text search index")

    # 3. Message citations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS message_citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            document_id INTEGER NOT NULL,
            page_number INTEGER,
            text_start INTEGER,
            text_end INTEGER,
            snippet TEXT,
            authority_name TEXT,
            authority_citation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """
    )
    print("✓ Created message_citations table")

    # Index for citation queries
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_citations_message 
        ON message_citations(message_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_citations_document 
        ON message_citations(document_id)
    """
    )

    # 4. Conversation topics table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            confidence REAL,  -- Topic extraction confidence score
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """
    )
    print("✓ Created conversation_topics table")

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_topics_conversation 
        ON conversation_topics(conversation_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_topics_topic 
        ON conversation_topics(topic)
    """
    )

    # 5. Conversation references table (track document usage)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            document_id INTEGER NOT NULL,
            page_number INTEGER,
            reference_count INTEGER DEFAULT 1,
            first_referenced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_referenced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            UNIQUE(conversation_id, document_id, page_number)
        )
    """
    )
    print("✓ Created conversation_references table")

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_references_conversation 
        ON conversation_references(conversation_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_references_document 
        ON conversation_references(document_id)
    """
    )

    # 6. Triggers for automatic updates

    # Update conversation.updated_at on new message
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_conversation_timestamp
        AFTER INSERT ON messages
        BEGIN
            UPDATE conversations 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.conversation_id;
        END
    """
    )
    print("✓ Created trigger: update_conversation_timestamp")

    # Sync messages to FTS index
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS messages_fts_insert
        AFTER INSERT ON messages
        BEGIN
            INSERT INTO messages_fts(message_id, role, content)
            VALUES (NEW.id, NEW.role, NEW.content);
        END
    """
    )

    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS messages_fts_delete
        AFTER DELETE ON messages
        BEGIN
            DELETE FROM messages_fts WHERE message_id = OLD.id;
        END
    """
    )
    print("✓ Created FTS sync triggers")

    # Update reference counts
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_reference_count
        AFTER INSERT ON message_citations
        BEGIN
            INSERT INTO conversation_references(conversation_id, document_id, page_number, reference_count, last_referenced)
            SELECT m.conversation_id, NEW.document_id, NEW.page_number, 1, CURRENT_TIMESTAMP
            FROM messages m
            WHERE m.id = NEW.message_id
            ON CONFLICT(conversation_id, document_id, page_number) DO UPDATE SET
                reference_count = reference_count + 1,
                last_referenced = CURRENT_TIMESTAMP;
        END
    """
    )
    print("✓ Created trigger: update_reference_count")

    conn.commit()

    # Verify conversation and message tables were created (excluding FTS internal tables)
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND (name LIKE 'conversation%' OR name='messages' OR name='message_citations')
        AND name NOT LIKE 'messages_fts_%'
        ORDER BY name
    """
    )

    tables = cursor.fetchall()
    print(f"\n✓ Migration complete! Created {len(tables)} core tables:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]} ({count} rows)")

    # Also verify FTS5 index exists
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='messages_fts'
    """
    )
    if cursor.fetchone():
        print("  - messages_fts (FTS5 index active)")

    conn.close()
    print(f"\nDatabase ready at: {db_path}")


if __name__ == "__main__":
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/Evident_legal.db"

    print("=" * 70)
    print("Enhanced Chat Database Migration")
    print("=" * 70)

    create_chat_tables(db_path)

    print("\n" + "=" * 70)
    print("Migration successful!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Register blueprint in app.py")
    print("2. Initialize pipeline with config")
    print("3. Test API endpoints")

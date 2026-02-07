# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Simple ChatGPT tables migration
Run with: python migrate_chatgpt_simple.py
"""

import os
import sys
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database path
instance_path = os.path.join(os.path.dirname(__file__), "instance")
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

db_path = os.path.join(instance_path, "Evident.db")
database_url = f"sqlite:///{db_path}"

print(f"Connecting to database: {db_path}")

# Create engine and session
engine = create_engine(database_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)


# Define ChatGPT models
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    custom_instructions = Column(Text)
    model_preference = Column(String(50), default="gpt-4")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, nullable=False)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer)
    model = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class UserApiKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    provider = Column(String(50), default="openai")
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def migrate():
    """Run migration"""

    print("\n🗄️  Creating ChatGPT integration tables...")

    try:
        # Create all tables
        Base.metadata.create_all(engine)

        print("\n✅ Migration complete! Tables created:")
        print("  ✓ projects")
        print("  ✓ conversations")
        print("  ✓ messages")
        print("  ✓ user_api_keys")

        print("\n📝 Next steps:")
        print("  1. ✅ ChatGPT blueprint registered in app.py")
        print("  2. ✅ openai and cryptography packages installed")
        print("  3. ✅ API_KEY_ENCRYPTION_KEY added to .env")
        print("  4. 🔄 Register ChatGPT services in MauiProgram.cs")
        print("  5. 🔄 Add ChatPage route to AppShell.xaml")
        print("  6. 🚀 Test the chat interface!")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)

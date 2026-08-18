# backend/app/services/ingestion/file_handler.py
import os
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings  # We will create this
from app.core.database import get_connection


# Define upload directory from settings
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def calculate_file_hash(file_content: bytes) -> str:
    """Generates a SHA-256 hash of the file content for idempotency."""
    return hashlib.sha256(file_content).hexdigest()

async def save_uploaded_file(upload_file: UploadFile) -> tuple[str, str, bytes]:
    """
    Saves the uploaded file to disk.
    Returns: (storage_path, file_hash, file_content_bytes)
    """
    # Read the entire file into memory (okay for MVP, we will stream later for huge files)
    content = await upload_file.read()
    
    # Generate hash before saving
    file_hash = calculate_file_hash(content)
    
    # Create a unique filename to avoid collisions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{upload_file.filename}"
    storage_path = UPLOAD_DIR / safe_filename
    
    # Write to disk
    with open(storage_path, "wb") as f:
        f.write(content)
    
    return str(storage_path), file_hash, content

def create_ingestion_batch(filename: str, file_hash: str, file_type: str) -> str:
    """Inserts a record into core.ingestion_batches and returns the batch_id."""
    batch_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO core.ingestion_batches 
                (id, filename, file_hash, file_type, status, uploaded_at)
                VALUES (%s, %s, %s, %s, 'pending', NOW())
            """, (batch_id, filename, file_hash, file_type))
            conn.commit()
    
    return batch_id

def update_batch_status(batch_id: str, status: str, error_message: str = None):
    """Updates the status of an ingestion batch."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            if error_message:
                cur.execute("""
                    UPDATE core.ingestion_batches 
                    SET status = %s, error_message = %s 
                    WHERE id = %s
                """, (status, error_message, batch_id))
            else:
                cur.execute("""
                    UPDATE core.ingestion_batches 
                    SET status = %s 
                    WHERE id = %s
                """, (status, batch_id))
            conn.commit()

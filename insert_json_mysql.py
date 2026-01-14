import json
import mysql.connector
from mysql.connector import Error
import openai
from dotenv import load_dotenv
import os
import time
from typing import List, Dict, Any
from pathlib import Path
import glob

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# MySQL Configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Nepal@2001",
    "database": "vector_db"
}

# Batch size for processing
BATCH_SIZE = 100
EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-ada-002"

# JSON templates folder path
JSON_TEMPLATES_FOLDER = "/Users/ebpearls/Desktop/Ai estimation/json_template"
JSON_TEMPLATES_FOLDER = "/Users/ebpearls/Desktop/Ai estimation/json_template"


def clear_table(cursor):
    """Clear all data from json_embeddings table"""
    try:
        cursor.execute("DELETE FROM json_embeddings")
        print("✅ Cleared all existing data from json_embeddings table")
    except Error as e:
        print(f"❌ Error clearing table: {e}")
        raise


def create_table(cursor):
    """Create a table to store JSON data with embeddings"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS json_embeddings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        estimation_id INT,
        estimation_name VARCHAR(500),
        epic_id INT,
        epic_name VARCHAR(500),
        task_name VARCHAR(500),
        platform VARCHAR(100),
        estimated_hour DECIMAL(10, 2),
        content_text TEXT,
        embedding BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_epic_id (epic_id),
        INDEX idx_estimation_id (estimation_id),
        UNIQUE KEY unique_record (estimation_id, epic_id, task_name, platform)
    )
    """
    cursor.execute(create_table_query)
    print("Table 'json_embeddings' created or already exists")


def flatten_json_data(json_data: List[Dict]) -> List[Dict]:
    """
    Flatten the nested JSON structure into individual records
    Each record will contain estimation, epic, task, and platform information
    """
    flattened_records = []
    
    for estimation in json_data:
        estimation_id = estimation.get('id')
        estimation_name = estimation.get('name', '')
        
        for epic in estimation.get('epics', []):
            epic_id = epic.get('id')
            epic_name = epic.get('name', '')
            
            for task in epic.get('tasks', []):
                task_name = task.get('name', '')
                
                # Skip tasks with null/empty names
                if not task_name:
                    continue
                
                for hour_info in task.get('hours', []):
                    platform = hour_info.get('platform', {}).get('name', '')
                    estimated_hour = hour_info.get('estimatedHour', 0)
                    
                    # Skip if no hours
                    if estimated_hour == 0:
                        continue
                    
                    # Create text for embedding - ONLY epic name and task name (NO HOURS!)
                    # This allows semantic search on epic/task names only
                    content_text = f"Epic: {epic_name}. Task: {task_name}"
                    
                    record = {
                        'estimation_id': estimation_id,
                        'estimation_name': estimation_name,
                        'epic_id': epic_id,
                        'epic_name': epic_name,
                        'task_name': task_name,
                        'platform': platform,
                        'estimated_hour': estimated_hour,
                        'content_text': content_text
                    }
                    flattened_records.append(record)
    
    return flattened_records


def get_embedding(text: str, retry_count: int = 3) -> List[float]:
    """
    Get embedding for a text using OpenAI API with retry logic
    """
    for attempt in range(retry_count):
        try:
            response = openai.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding (attempt {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise


def insert_batch(cursor, records: List[Dict]):
    """
    Insert a batch of records with embeddings into MySQL
    """
    insert_query = """
    INSERT INTO json_embeddings 
    (estimation_id, estimation_name, epic_id, epic_name, task_name, platform, 
     estimated_hour, content_text, embedding)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    batch_data = []
    for record in records:
        try:
            # Get embedding for the content text
            embedding = get_embedding(record['content_text'])
            
            # Convert embedding to bytes for BLOB storage
            embedding_bytes = json.dumps(embedding).encode('utf-8')
            
            batch_data.append((
                record['estimation_id'],
                record['estimation_name'],
                record['epic_id'],
                record['epic_name'],
                record['task_name'],
                record['platform'],
                record['estimated_hour'],
                record['content_text'],
                embedding_bytes
            ))
            
        except Exception as e:
            print(f"Error processing record: {e}")
            continue
    
    if batch_data:
        cursor.executemany(insert_query, batch_data)
        print(f"Inserted {len(batch_data)} records")
        return len(batch_data)
    return 0


def get_all_json_files(folder_path: str) -> List[str]:
    """
    Get all JSON files from the specified folder
    """
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    return sorted(json_files)


def process_json_file(file_path: str, cursor, conn) -> Dict[str, int]:
    """
    Process a single JSON file and insert its data into MySQL
    Returns statistics about the processing
    """
    stats = {
        'estimations': 0,
        'records': 0,
        'inserted': 0
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(file_path)}")
        print(f"{'='*60}")
        
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        
        stats['estimations'] = len(json_data)
        print(f"✓ Loaded {stats['estimations']} estimations from file")
        
        # Flatten JSON data
        flattened_records = flatten_json_data(json_data)
        stats['records'] = len(flattened_records)
        print(f"✓ Created {stats['records']} flattened records")
        
        if stats['records'] == 0:
            print("⚠️  No records to process in this file")
            return stats
        
        # Process records in batches
        total_inserted = 0
        for i in range(0, stats['records'], BATCH_SIZE):
            batch = flattened_records[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (stats['records'] + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"\nProcessing batch {batch_num}/{total_batches} "
                  f"(records {i + 1}-{min(i + BATCH_SIZE, stats['records'])})...")
            
            try:
                inserted = insert_batch(cursor, batch)
                total_inserted += inserted
                conn.commit()
            except Exception as e:
                print(f"❌ Error inserting batch: {e}")
                conn.rollback()
            
            # Rate limiting - avoid hitting API limits
            time.sleep(1)
        
        stats['inserted'] = total_inserted
        
        print(f"\n✅ File processed successfully!")
        print(f"   - Total records: {stats['records']}")
        print(f"   - Inserted: {stats['inserted']}")
        
    except Exception as e:
        print(f"❌ Error processing file {file_path}: {e}")
    
    return stats


def main():
    print("="*60)
    print("JSON to MySQL Embedding Pipeline")
    print("="*60)
    
    # Check if JSON templates folder exists
    if not os.path.exists(JSON_TEMPLATES_FOLDER):
        print(f"❌ Error: Folder not found: {JSON_TEMPLATES_FOLDER}")
        return
    
    # Get all JSON files
    json_files = get_all_json_files(JSON_TEMPLATES_FOLDER)
    
    if not json_files:
        print(f"❌ No JSON files found in: {JSON_TEMPLATES_FOLDER}")
        return
    
    print(f"\n📂 Found {len(json_files)} JSON file(s) to process:")
    for i, file_path in enumerate(json_files, 1):
        print(f"   {i}. {os.path.basename(file_path)}")
    
    # Connect to MySQL
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            print(f"\n✓ Connected to MySQL database: {MYSQL_CONFIG['database']}")
            cursor = conn.cursor()
            
            # Create table with unique constraint
            create_table(cursor)
            
            # Get initial count
            cursor.execute("SELECT COUNT(*) FROM json_embeddings")
            initial_count = cursor.fetchone()[0]
            print(f"✓ Current records in database: {initial_count}")
            
            # Clear existing data
            print("\n🗑️  Clearing existing data...")
            clear_table(cursor)
            conn.commit()
            
            # Process all JSON files
            total_stats = {
                'files_processed': 0,
                'total_estimations': 0,
                'total_records': 0,
                'total_inserted': 0
            }
            
            for file_path in json_files:
                stats = process_json_file(file_path, cursor, conn)
                total_stats['files_processed'] += 1
                total_stats['total_estimations'] += stats['estimations']
                total_stats['total_records'] += stats['records']
                total_stats['total_inserted'] += stats['inserted']
            
            # Show final summary
            print(f"\n{'='*60}")
            print("FINAL SUMMARY")
            print(f"{'='*60}")
            print(f"✓ Files processed: {total_stats['files_processed']}")
            print(f"✓ Total estimations: {total_stats['total_estimations']}")
            print(f"✓ Total records processed: {total_stats['total_records']}")
            print(f"✓ Records inserted: {total_stats['total_inserted']}")
            
            # Get final count
            cursor.execute("SELECT COUNT(*) FROM json_embeddings")
            final_count = cursor.fetchone()[0]
            print(f"\n📊 Database Statistics:")
            print(f"   - Before: {initial_count} records")
            print(f"   - After: {final_count} records")
            print(f"   - Added: {final_count - initial_count} records")
            
            print(f"\n{'='*60}")
            print("✅ ALL FILES PROCESSED SUCCESSFULLY!")
            print(f"{'='*60}")
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("\n✓ MySQL connection closed")


if __name__ == "__main__":
    main()

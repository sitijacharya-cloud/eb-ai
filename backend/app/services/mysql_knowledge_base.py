"""
MySQL Vector Knowledge Base Service
Replaces ChromaDB with MySQL for vector embeddings
"""

import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import mysql.connector
from mysql.connector import Error
import numpy as np
import openai
from dotenv import load_dotenv

from ..models.schemas import Epic, Task, Platform

# Load environment
load_dotenv()

logger = logging.getLogger(__name__)

# MySQL Configuration
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Nepal@2001"),
    "database": os.getenv("MYSQL_DATABASE", "vector_db")
}

EMBEDDING_MODEL = "text-embedding-3-small"


class MySQLKnowledgeBase:
    """MySQL-based vector knowledge base for epic templates"""
    
    def __init__(self):
        """Initialize MySQL knowledge base"""
        self.config = MYSQL_CONFIG
        openai.api_key = os.getenv("OPENAI_API_KEY")
        logger.info("Initialized MySQL Knowledge Base")
    
    def _get_connection(self):
        """Get MySQL connection"""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            logger.error(f"MySQL connection error: {e}")
            raise
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API"""
        try:
            response = openai.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def load_templates_from_directory(self, templates_dir: str = "data/templates"):
        """
        Load JSON templates into MySQL database
        
        Args:
            templates_dir: Directory containing JSON template files
        """
        logger.info(f"Loading templates from: {templates_dir}")
        
        templates_path = Path(templates_dir)
        if not templates_path.exists():
            logger.error(f"Templates directory not found: {templates_dir}")
            return
        
        # Get all JSON files
        json_files = list(templates_path.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON template files")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # cursor.execute("DELETE FROM json_embeddings WHERE estimation_name LIKE 'Template:%'")
        # conn.commit()
        # logger.info("Cleared existing template data")
        
        total_epics = 0
        
        for json_file in json_files:
            try:
                logger.info(f"Processing: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                template_name = template_data.get("template_name", json_file.stem)
                domain = template_data.get("domain", "general")
                epics_data = template_data.get("epics", {})
                
                # Generate a unique estimation_id for this template
                cursor.execute("SELECT COALESCE(MAX(estimation_id), 0) + 1 FROM json_embeddings")
                estimation_id = cursor.fetchone()[0]
                
                epic_id_counter = 1
                
                for epic_name, tasks_dict in epics_data.items():
                    epic_id = epic_id_counter
                    epic_id_counter += 1
                    
                    # Generate embedding for epic name
                    epic_embedding = self._get_embedding(epic_name)
                    epic_embedding_json = json.dumps(epic_embedding)
                    
                    for task_name, platforms_dict in tasks_dict.items():
                        for platform, hours in platforms_dict.items():
                            # Content text for this record
                            content_text = f"Epic: {epic_name}. Task: {task_name}. Platform: {platform}"
                            
                            # Insert into database
                            cursor.execute("""
                                INSERT INTO json_embeddings 
                                (estimation_id, estimation_name, epic_id, epic_name, 
                                 task_name, platform, estimated_hour, content_text, embedding)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                estimation_id,
                                f"Template: {template_name}",
                                epic_id,
                                epic_name,
                                task_name,
                                platform,
                                float(hours),
                                content_text,
                                epic_embedding_json.encode('utf-8')
                            ))
                    
                    total_epics += 1
                
                conn.commit()
                logger.info(f"  ✓ Loaded {len(epics_data)} epics from {template_name}")
                
            except Exception as e:
                logger.error(f"Error loading {json_file.name}: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
        logger.info(f"✓ Total templates loaded: {len(json_files)}, Total epics: {total_epics}")
    
    def retrieve_similar_epics(
        self, 
        query_text: str, 
        n_results: int = 3,
        similarity_threshold: float = 0.4
    ) -> List[Epic]:
        """
        Retrieve similar epics based on query using vector similarity
        
        Args:
            query_text: Search query text
            n_results: Maximum number of epics to return
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of Epic objects with tasks
        """
        logger.info(f"Searching for similar epics: '{query_text[:100]}'...")
        
        # Generate embedding for query
        query_embedding = self._get_embedding(query_text)
        
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch all unique epics with their embeddings
        cursor.execute("""
            SELECT DISTINCT epic_id, epic_name, estimation_name,
                   (SELECT embedding FROM json_embeddings e2 
                    WHERE e2.epic_id = e1.epic_id 
                    AND e2.estimation_name = e1.estimation_name
                    LIMIT 1) as embedding
            FROM json_embeddings e1
        """)
        
        epic_records = cursor.fetchall()
        
        # Calculate similarity for each epic
        epic_similarities = []
        
        for epic_record in epic_records:
            try:
                embedding = json.loads(epic_record['embedding'].decode('utf-8'))
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                if similarity >= similarity_threshold:
                    epic_similarities.append({
                        'epic_id': epic_record['epic_id'],
                        'epic_name': epic_record['epic_name'],
                        'estimation_name': epic_record['estimation_name'],
                        'similarity': similarity
                    })
            except Exception as e:
                logger.warning(f"Error processing epic {epic_record['epic_name']}: {e}")
                continue
        
        # Sort by similarity and limit results
        epic_similarities.sort(key=lambda x: x['similarity'], reverse=True)
        epic_similarities = epic_similarities[:n_results]
        
        logger.info(f"Found {len(epic_similarities)} similar epics")
        
        # Fetch all tasks for matching epics
        result_epics = []
        
        for epic_info in epic_similarities:
            # Get all tasks for this epic
            cursor.execute("""
                SELECT task_name, platform, estimated_hour
                FROM json_embeddings
                WHERE epic_id = %s AND estimation_name = %s
                ORDER BY task_name, platform
            """, (epic_info['epic_id'], epic_info['estimation_name']))
            
            task_records = cursor.fetchall()
            
            # Group by task_name
            tasks_dict = {}
            for record in task_records:
                task_name = record['task_name']
                if task_name not in tasks_dict:
                    tasks_dict[task_name] = {}
                
                platform_name = record['platform']
                estimated_hour = record['estimated_hour']
                
                # Map "Web Service" to "API" for compatibility
                if platform_name == "Web Service":
                    platform_name = "API"
                
                # Map "Designer" to "CMS" for compatibility
                if platform_name == "Designer":
                    platform_name = "CMS"
                
                try:
                    # Try to match with Platform enum
                    platform = Platform(platform_name)
                    tasks_dict[task_name][platform] = int(float(estimated_hour))
                except (ValueError, KeyError):
                    # If platform not in enum, log warning and skip
                    logger.debug(f"Skipping unknown platform '{platform_name}' for task '{task_name}'")
                    continue
            
            # Create Task objects
            tasks = []
            for task_name, efforts in tasks_dict.items():
                task = Task(
                    description=task_name,
                    efforts=efforts,
                    source=epic_info['estimation_name'],
                    is_custom=False
                )
                tasks.append(task)
            
            # Create Epic object
            epic = Epic(
                name=epic_info['epic_name'],
                description=f"From {epic_info['estimation_name']}",
                tasks=tasks,
                is_mandatory=False,
                source_template=epic_info['estimation_name']
            )
            
            result_epics.append(epic)
        
        cursor.close()
        conn.close()
        
        return result_epics
    
    def get_epic_by_name(
        self, 
        epic_name: str, 
        template_name: Optional[str] = None
    ) -> Optional[Epic]:
        """
        Get a specific epic by name
        
        Args:
            epic_name: Name of the epic
            template_name: Optional template name to filter by
            
        Returns:
            Epic object or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build query
        query = """
            SELECT DISTINCT epic_id, epic_name, estimation_name
            FROM json_embeddings
            WHERE epic_name = %s
        """
        params = [epic_name]
        
        if template_name:
            query += " AND estimation_name = %s"
            params.append(f"Template: {template_name}")
        
        query += " LIMIT 1"
        
        cursor.execute(query, params)
        epic_record = cursor.fetchone()
        
        if not epic_record:
            logger.warning(f"Epic not found: {epic_name}")
            cursor.close()
            conn.close()
            return None
        
        # Fetch all tasks for this epic
        cursor.execute("""
            SELECT task_name, platform, estimated_hour
            FROM json_embeddings
            WHERE epic_id = %s AND estimation_name = %s
            ORDER BY task_name, platform
        """, (epic_record['epic_id'], epic_record['estimation_name']))
        
        task_records = cursor.fetchall()
        
        # Group by task_name
        tasks_dict = {}
        for record in task_records:
            task_name = record['task_name']
            if task_name not in tasks_dict:
                tasks_dict[task_name] = {}
            
            try:
                platform = Platform(record['platform'])
                tasks_dict[task_name][platform] = int(float(record['estimated_hour']))
            except (ValueError, KeyError):
                pass
        
        # Create Task objects
        tasks = []
        for task_name, efforts in tasks_dict.items():
            task = Task(
                description=task_name,
                efforts=efforts,
                source=epic_record['estimation_name'],
                is_custom=False
            )
            tasks.append(task)
        
        # Create Epic object
        epic = Epic(
            name=epic_record['epic_name'],
            description=f"From {epic_record['estimation_name']}",
            tasks=tasks,
            is_mandatory=False,
            source_template=epic_record['estimation_name']
        )
        
        cursor.close()
        conn.close()
        
        return epic
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total epics
        cursor.execute("""
            SELECT COUNT(DISTINCT CONCAT(epic_id, '-', estimation_name)) as total_epics
            FROM json_embeddings
        """)
        total_epics = cursor.fetchone()['total_epics']
        
        # Total templates
        cursor.execute("""
            SELECT COUNT(DISTINCT estimation_name) as total_templates
            FROM json_embeddings
        """)
        total_templates = cursor.fetchone()['total_templates']
        
        # Get template names
        cursor.execute("""
            SELECT DISTINCT estimation_name
            FROM json_embeddings
            ORDER BY estimation_name
        """)
        templates = [row['estimation_name'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "total_epics": total_epics,
            "total_templates": total_templates,
            "templates": templates
        }


# Singleton instance
_kb_instance = None

def get_knowledge_base() -> MySQLKnowledgeBase:
    """Get or create knowledge base instance"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = MySQLKnowledgeBase()
    return _kb_instance


# CLI for loading templates
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    kb = get_knowledge_base()
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        print("Initializing MySQL knowledge base...")
        kb.load_templates_from_directory()
        
        stats = kb.get_stats()
        print(f"\n✓ Loaded {stats['total_epics']} epics from {stats['total_templates']} templates")
        print(f"✓ Templates: {', '.join(stats['templates'])}")
    else:
        print("Usage: python -m backend.app.services.mysql_knowledge_base init")

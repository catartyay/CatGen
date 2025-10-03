"""
Database layer using SQLite for efficient cat registry storage and querying
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from core.cat import Cat

logger = logging.getLogger('catgen.database')


class DatabaseManager:
    """
    SQLite database manager for cat registry
    Provides efficient storage, querying, and transaction management
    """
    
    def __init__(self, db_path: str = "data/catgen.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self._create_tables()
        self._create_indexes()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def _create_tables(self):
        """Create database tables"""
        # Cats table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS cats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                sex TEXT NOT NULL CHECK(sex IN ('male', 'female')),
                genes TEXT NOT NULL,
                birth_date TEXT,
                sire_id INTEGER,
                dam_id INTEGER,
                build_value INTEGER CHECK(build_value BETWEEN 0 AND 100),
                size_value INTEGER CHECK(size_value BETWEEN 0 AND 100),
                white_percentage INTEGER CHECK(white_percentage BETWEEN 0 AND 100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (sire_id) REFERENCES cats(id) ON DELETE SET NULL,
                FOREIGN KEY (dam_id) REFERENCES cats(id) ON DELETE SET NULL
            )
        ''')
        
        # Litters table for tracking breeding history
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS litters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sire_id INTEGER NOT NULL,
                dam_id INTEGER NOT NULL,
                breeding_date TEXT NOT NULL,
                litter_size INTEGER NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sire_id) REFERENCES cats(id),
                FOREIGN KEY (dam_id) REFERENCES cats(id)
            )
        ''')
        
        # Litter members junction table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS litter_members (
                litter_id INTEGER NOT NULL,
                cat_id INTEGER NOT NULL,
                PRIMARY KEY (litter_id, cat_id),
                FOREIGN KEY (litter_id) REFERENCES litters(id) ON DELETE CASCADE,
                FOREIGN KEY (cat_id) REFERENCES cats(id) ON DELETE CASCADE
            )
        ''')
        
        # Phenotype cache table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS phenotype_cache (
                cat_id INTEGER PRIMARY KEY,
                phenotype TEXT NOT NULL,
                eye_color TEXT NOT NULL,
                white_description TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cat_id) REFERENCES cats(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_cats_sex ON cats(sex)",
            "CREATE INDEX IF NOT EXISTS idx_cats_sire ON cats(sire_id)",
            "CREATE INDEX IF NOT EXISTS idx_cats_dam ON cats(dam_id)",
            "CREATE INDEX IF NOT EXISTS idx_cats_birth ON cats(birth_date)",
            "CREATE INDEX IF NOT EXISTS idx_cats_name ON cats(name)",
            "CREATE INDEX IF NOT EXISTS idx_litters_sire ON litters(sire_id)",
            "CREATE INDEX IF NOT EXISTS idx_litters_dam ON litters(dam_id)",
            "CREATE INDEX IF NOT EXISTS idx_litters_date ON litters(breeding_date)"
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
        
        self.conn.commit()
    
    def insert_cat(self, cat: Cat) -> int:
        """
        Insert a new cat into the database
        
        Args:
            cat: Cat object to insert
            
        Returns:
            The assigned cat ID
        """
        cursor = self.conn.execute('''
            INSERT INTO cats (
                name, sex, genes, birth_date, sire_id, dam_id,
                build_value, size_value, white_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cat.name,
            cat.sex,
            json.dumps(cat.genes),
            cat.birth_date,
            cat.sire_id,
            cat.dam_id,
            cat.build_value,
            cat.size_value,
            cat._white_percentage
        ))
        
        self.conn.commit()
        cat_id = cursor.lastrowid
        
        logger.debug(f"Inserted cat #{cat_id}")
        return cat_id
    
    def update_cat(self, cat: Cat) -> bool:
        """Update an existing cat"""
        if not cat.id:
            raise ValueError("Cat must have an ID to update")
        
        self.conn.execute('''
            UPDATE cats SET
                name = ?,
                sex = ?,
                genes = ?,
                birth_date = ?,
                sire_id = ?,
                dam_id = ?,
                build_value = ?,
                size_value = ?,
                white_percentage = ?,
                modified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            cat.name,
            cat.sex,
            json.dumps(cat.genes),
            cat.birth_date,
            cat.sire_id,
            cat.dam_id,
            cat.build_value,
            cat.size_value,
            cat._white_percentage,
            cat.id
        ))
        
        self.conn.commit()
        
        # Invalidate phenotype cache
        self.conn.execute('DELETE FROM phenotype_cache WHERE cat_id = ?', (cat.id,))
        self.conn.commit()
        
        logger.debug(f"Updated cat #{cat.id}")
        return True
    
    def delete_cat(self, cat_id: int) -> bool:
        """Delete a cat from the database"""
        cursor = self.conn.execute('DELETE FROM cats WHERE id = ?', (cat_id,))
        self.conn.commit()
        
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Deleted cat #{cat_id}")
        
        return deleted
    
    def get_cat(self, cat_id: int) -> Optional[Cat]:
        """Get a cat by ID"""
        cursor = self.conn.execute('SELECT * FROM cats WHERE id = ?', (cat_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_cat(row)
        return None
    
    def get_all_cats(self) -> List[Cat]:
        """Get all cats"""
        cursor = self.conn.execute('SELECT * FROM cats ORDER BY id')
        return [self._row_to_cat(row) for row in cursor.fetchall()]
    
    def query_cats(self, filters: Dict[str, Any]) -> List[Cat]:
        """
        Query cats with flexible filters
        
        Args:
            filters: Dictionary of filter criteria
                - sex: 'male' or 'female'
                - has_parents: bool
                - has_offspring: bool
                - search: text search in name or ID
                - min_id, max_id: ID range
                - birth_after, birth_before: date range
                
        Returns:
            List of matching cats
        """
        query = "SELECT * FROM cats WHERE 1=1"
        params = []
        
        # Sex filter
        if 'sex' in filters and filters['sex'] in ['male', 'female']:
            query += " AND sex = ?"
            params.append(filters['sex'])
        
        # Parents filter
        if filters.get('has_parents'):
            query += " AND (sire_id IS NOT NULL OR dam_id IS NOT NULL)"
        elif 'has_parents' in filters and not filters['has_parents']:
            query += " AND sire_id IS NULL AND dam_id IS NULL"
        
        # Offspring filter (requires subquery)
        if filters.get('has_offspring'):
            query += " AND id IN (SELECT DISTINCT sire_id FROM cats WHERE sire_id IS NOT NULL UNION SELECT DISTINCT dam_id FROM cats WHERE dam_id IS NOT NULL)"
        
        # Text search
        if 'search' in filters and filters['search']:
            search_term = f"%{filters['search']}%"
            query += " AND (name LIKE ? OR CAST(id AS TEXT) LIKE ?)"
            params.extend([search_term, search_term])
        
        # ID range
        if 'min_id' in filters:
            query += " AND id >= ?"
            params.append(filters['min_id'])
        if 'max_id' in filters:
            query += " AND id <= ?"
            params.append(filters['max_id'])
        
        # Date range
        if 'birth_after' in filters:
            query += " AND birth_date >= ?"
            params.append(filters['birth_after'])
        if 'birth_before' in filters:
            query += " AND birth_date <= ?"
            params.append(filters['birth_before'])
        
        # Execute query
        cursor = self.conn.execute(query, params)
        return [self._row_to_cat(row) for row in cursor.fetchall()]
    
    def get_offspring(self, parent_id: int) -> List[Cat]:
        """Get all offspring of a cat"""
        cursor = self.conn.execute(
            'SELECT * FROM cats WHERE sire_id = ? OR dam_id = ?',
            (parent_id, parent_id)
        )
        return [self._row_to_cat(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {}
        
        # Total cats
        cursor = self.conn.execute('SELECT COUNT(*) FROM cats')
        stats['total'] = cursor.fetchone()[0]
        
        # By sex
        cursor = self.conn.execute(
            "SELECT sex, COUNT(*) FROM cats GROUP BY sex"
        )
        for row in cursor:
            stats[f'{row[0]}s'] = row[1]
        
        # Founders (no parents)
        cursor = self.conn.execute(
            'SELECT COUNT(*) FROM cats WHERE sire_id IS NULL AND dam_id IS NULL'
        )
        stats['founders'] = cursor.fetchone()[0]
        
        # With parents
        cursor = self.conn.execute(
            'SELECT COUNT(*) FROM cats WHERE sire_id IS NOT NULL OR dam_id IS NOT NULL'
        )
        stats['with_parents'] = cursor.fetchone()[0]
        
        return stats
    
    def cache_phenotype(self, cat_id: int, phenotype: str, eye_color: str,
                       white_desc: Optional[str] = None):
        """Cache calculated phenotype for performance"""
        self.conn.execute('''
            INSERT OR REPLACE INTO phenotype_cache 
            (cat_id, phenotype, eye_color, white_description, calculated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (cat_id, phenotype, eye_color, white_desc))
        
        self.conn.commit()
    
    def get_cached_phenotype(self, cat_id: int) -> Optional[Dict]:
        """Get cached phenotype if available"""
        cursor = self.conn.execute(
            'SELECT phenotype, eye_color, white_description FROM phenotype_cache WHERE cat_id = ?',
            (cat_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'phenotype': row[0],
                'eye_color': row[1],
                'white_description': row[2]
            }
        return None
    
    def record_litter(self, sire_id: int, dam_id: int, 
                     kitten_ids: List[int], notes: str = "") -> int:
        """Record a breeding litter"""
        cursor = self.conn.execute('''
            INSERT INTO litters (sire_id, dam_id, breeding_date, litter_size, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            sire_id,
            dam_id,
            datetime.now().strftime('%Y-%m-%d'),
            len(kitten_ids),
            notes
        ))
        
        litter_id = cursor.lastrowid
        
        # Add litter members
        for kitten_id in kitten_ids:
            self.conn.execute(
                'INSERT INTO litter_members (litter_id, cat_id) VALUES (?, ?)',
                (litter_id, kitten_id)
            )
        
        self.conn.commit()
        logger.info(f"Recorded litter #{litter_id}: {len(kitten_ids)} kittens")
        
        return litter_id
    
    def get_litter_history(self, cat_id: int) -> List[Dict]:
        """Get breeding history for a cat"""
        cursor = self.conn.execute('''
            SELECT l.*, 
                   (SELECT COUNT(*) FROM litter_members WHERE litter_id = l.id) as actual_size
            FROM litters l
            WHERE l.sire_id = ? OR l.dam_id = ?
            ORDER BY l.breeding_date DESC
        ''', (cat_id, cat_id))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        logger.info(f"Database backed up to {backup_path}")
    
    def vacuum(self):
        """Optimize database (reclaim space, rebuild indexes)"""
        self.conn.execute('VACUUM')
        self.conn.commit()
        logger.info("Database vacuumed")
    
    def _row_to_cat(self, row: sqlite3.Row) -> Cat:
        """Convert database row to Cat object"""
        return Cat(
            cat_id=row['id'],
            name=row['name'],
            sex=row['sex'],
            genes=json.loads(row['genes']),
            birth_date=row['birth_date'],
            sire_id=row['sire_id'],
            dam_id=row['dam_id'],
            build_value=row['build_value'],
            size_value=row['size_value'],
            white_percentage=row['white_percentage']
        )
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("Database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
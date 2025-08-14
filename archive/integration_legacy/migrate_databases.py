"""
🔄 Database Migration Utility
Addresses critical system need: unify skill tree schema with main database
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self):
        self.main_db = "dsatrain_phase4.db"
        self.skill_tree_db = "dsatrain_skilltree.db"
        self.backup_suffix = f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    def backup_databases(self):
        """Create backups of both databases"""
        logger.info("📋 Creating database backups...")
        
        try:
            # Backup main database
            main_backup = self.main_db.replace('.db', self.backup_suffix)
            shutil.copy2(self.main_db, main_backup)
            logger.info(f"✅ Main DB backed up to: {main_backup}")
            
            # Backup skill tree database
            skill_backup = self.skill_tree_db.replace('.db', self.backup_suffix)
            shutil.copy2(self.skill_tree_db, skill_backup)
            logger.info(f"✅ Skill tree DB backed up to: {skill_backup}")
            
            return main_backup, skill_backup
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            raise
    
    def check_schema_differences(self):
        """Analyze schema differences between databases"""
        logger.info("🔍 Analyzing schema differences...")
        
        try:
            # Get main DB schema
            main_conn = sqlite3.connect(self.main_db)
            main_cursor = main_conn.cursor()
            
            main_cursor.execute("PRAGMA table_info(problems)")
            main_columns = {row[1]: row[2] for row in main_cursor.fetchall()}
            
            # Get skill tree DB schema
            skill_conn = sqlite3.connect(self.skill_tree_db)
            skill_cursor = skill_conn.cursor()
            
            skill_cursor.execute("PRAGMA table_info(problems)")
            skill_columns = {row[1]: row[2] for row in skill_cursor.fetchall()}
            
            # Find differences
            missing_in_main = set(skill_columns.keys()) - set(main_columns.keys())
            extra_in_skill = set(skill_columns.keys()) - set(main_columns.keys())
            
            logger.info(f"📊 Main DB has {len(main_columns)} columns in problems table")
            logger.info(f"📊 Skill tree DB has {len(skill_columns)} columns in problems table")
            logger.info(f"📊 Missing in main DB: {missing_in_main}")
            
            main_conn.close()
            skill_conn.close()
            
            return missing_in_main, main_columns, skill_columns
            
        except Exception as e:
            logger.error(f"❌ Schema analysis failed: {e}")
            raise
    
    def add_missing_columns(self, missing_columns, skill_columns):
        """Add missing skill tree columns to main database"""
        logger.info("🔧 Adding missing columns to main database...")
        
        try:
            conn = sqlite3.connect(self.main_db)
            cursor = conn.cursor()
            
            # Column definitions for skill tree fields
            column_definitions = {
                'sub_difficulty_level': 'INTEGER',
                'conceptual_difficulty': 'INTEGER',
                'implementation_complexity': 'INTEGER',
                'prerequisite_skills': 'JSON',
                'skill_tree_position': 'JSON'
            }
            
            for column in missing_columns:
                if column in column_definitions:
                    data_type = column_definitions[column]
                    sql = f"ALTER TABLE problems ADD COLUMN {column} {data_type}"
                    logger.info(f"Adding column: {column} ({data_type})")
                    cursor.execute(sql)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Successfully added missing columns to main database")
            
        except Exception as e:
            logger.error(f"❌ Column addition failed: {e}")
            raise
    
    def migrate_skill_tree_data(self):
        """Copy skill tree data from skill tree DB to main DB"""
        logger.info("📊 Migrating skill tree data...")
        
        try:
            # Connect to both databases
            main_conn = sqlite3.connect(self.main_db)
            skill_conn = sqlite3.connect(self.skill_tree_db)
            
            main_cursor = main_conn.cursor()
            skill_cursor = skill_conn.cursor()
            
            # Get all skill tree problems with enhanced data
            skill_cursor.execute("""
                SELECT id, sub_difficulty_level, conceptual_difficulty, 
                       implementation_complexity, prerequisite_skills, 
                       skill_tree_position
                FROM problems 
                WHERE sub_difficulty_level IS NOT NULL
            """)
            
            skill_data = skill_cursor.fetchall()
            logger.info(f"📊 Found {len(skill_data)} problems with skill tree data")
            
            # Update main database with skill tree data
            updated_count = 0
            for row in skill_data:
                problem_id, sub_diff, concept_diff, impl_complex, prereq_skills, tree_pos = row
                
                # Check if problem exists in main DB
                main_cursor.execute("SELECT id FROM problems WHERE id = ?", (problem_id,))
                if main_cursor.fetchone():
                    # Update existing problem
                    main_cursor.execute("""
                        UPDATE problems 
                        SET sub_difficulty_level = ?, 
                            conceptual_difficulty = ?,
                            implementation_complexity = ?,
                            prerequisite_skills = ?,
                            skill_tree_position = ?
                        WHERE id = ?
                    """, (sub_diff, concept_diff, impl_complex, prereq_skills, tree_pos, problem_id))
                    updated_count += 1
                else:
                    logger.warning(f"⚠️ Problem {problem_id} not found in main database")
            
            main_conn.commit()
            
            logger.info(f"✅ Updated {updated_count} problems with skill tree data")
            
            main_conn.close()
            skill_conn.close()
            
            return updated_count
            
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            raise
    
    def create_missing_tables(self):
        """Create skill tree specific tables in main database"""
        logger.info("🏗️ Creating missing skill tree tables...")
        
        try:
            conn = sqlite3.connect(self.main_db)
            cursor = conn.cursor()
            
            # Create problem_clusters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS problem_clusters (
                    id TEXT PRIMARY KEY,
                    cluster_name TEXT,
                    primary_skill_area TEXT,
                    difficulty_level TEXT,
                    representative_problems JSON,
                    cluster_size INTEGER,
                    avg_quality_score REAL,
                    similarity_threshold REAL,
                    algorithm_tags JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user_problem_confidence table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_problem_confidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    problem_id TEXT,
                    confidence_level INTEGER,
                    solve_time_seconds INTEGER,
                    hints_used INTEGER,
                    attempts_count INTEGER DEFAULT 1,
                    last_attempted TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (problem_id) REFERENCES problems (id)
                )
            """)
            
            # Create user_skill_mastery table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_skill_mastery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    skill_area TEXT,
                    mastery_level REAL DEFAULT 0.0,
                    problems_attempted INTEGER DEFAULT 0,
                    problems_solved INTEGER DEFAULT 0,
                    avg_confidence REAL DEFAULT 0.0,
                    mastery_trend REAL DEFAULT 0.0,
                    last_activity TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user_skill_tree_preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_skill_tree_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    preferred_view_mode TEXT DEFAULT 'columns',
                    show_confidence_overlay BOOLEAN DEFAULT TRUE,
                    auto_expand_clusters BOOLEAN DEFAULT FALSE,
                    highlight_prerequisites BOOLEAN DEFAULT TRUE,
                    visible_skill_areas JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Successfully created skill tree tables")
            
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            raise
    
    def migrate_additional_data(self):
        """Migrate clusters and other skill tree data"""
        logger.info("📊 Migrating additional skill tree data...")
        
        try:
            main_conn = sqlite3.connect(self.main_db)
            skill_conn = sqlite3.connect(self.skill_tree_db)
            
            # Copy problem clusters
            skill_conn.execute("SELECT * FROM problem_clusters")
            clusters = skill_conn.fetchall()
            
            if clusters:
                # Get column names
                skill_conn.execute("PRAGMA table_info(problem_clusters)")
                columns = [col[1] for col in skill_conn.fetchall()]
                
                placeholders = ','.join(['?' for _ in columns])
                column_names = ','.join(columns)
                
                main_conn.executemany(
                    f"INSERT OR REPLACE INTO problem_clusters ({column_names}) VALUES ({placeholders})",
                    clusters
                )
                
                logger.info(f"✅ Migrated {len(clusters)} problem clusters")
            
            main_conn.commit()
            main_conn.close()
            skill_conn.close()
            
        except Exception as e:
            logger.error(f"❌ Additional data migration failed: {e}")
            # Don't raise - this is non-critical
    
    def verify_migration(self):
        """Verify migration was successful"""
        logger.info("🔍 Verifying migration results...")
        
        try:
            conn = sqlite3.connect(self.main_db)
            cursor = conn.cursor()
            
            # Check problems table has skill tree columns
            cursor.execute("PRAGMA table_info(problems)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            skill_tree_columns = [
                'sub_difficulty_level', 'conceptual_difficulty', 
                'implementation_complexity', 'prerequisite_skills', 
                'skill_tree_position'
            ]
            
            missing = [col for col in skill_tree_columns if col not in columns]
            if missing:
                logger.error(f"❌ Missing columns after migration: {missing}")
                return False
            
            # Check data
            cursor.execute("SELECT COUNT(*) FROM problems WHERE sub_difficulty_level IS NOT NULL")
            enhanced_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM problems")
            total_count = cursor.fetchone()[0]
            
            logger.info(f"✅ Migration verification successful:")
            logger.info(f"  📊 Total problems: {total_count}")
            logger.info(f"  🌳 Problems with skill tree data: {enhanced_count}")
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'problems', 'problem_clusters', 'user_problem_confidence',
                'user_skill_mastery', 'user_skill_tree_preferences'
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
            
            logger.info(f"✅ All required tables present: {required_tables}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False
    
    def run_full_migration(self):
        """Run complete database migration process"""
        logger.info("🚀 Starting full database migration...")
        
        try:
            # Step 1: Backup databases
            main_backup, skill_backup = self.backup_databases()
            
            # Step 2: Analyze schema differences
            missing_columns, main_columns, skill_columns = self.check_schema_differences()
            
            # Step 3: Add missing columns to main database
            if missing_columns:
                self.add_missing_columns(missing_columns, skill_columns)
            else:
                logger.info("ℹ️ No missing columns found")
            
            # Step 4: Create missing tables
            self.create_missing_tables()
            
            # Step 5: Migrate skill tree data
            updated_count = self.migrate_skill_tree_data()
            
            # Step 6: Migrate additional data
            self.migrate_additional_data()
            
            # Step 7: Verify migration
            success = self.verify_migration()
            
            if success:
                logger.info("🎉 Database migration completed successfully!")
                logger.info(f"📊 Updated {updated_count} problems with skill tree data")
                logger.info(f"💾 Backups created: {main_backup}, {skill_backup}")
                return True
            else:
                logger.error("❌ Migration verification failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False

def main():
    """Main migration execution"""
    print("🔄 DSA Train Database Migration Utility")
    print("=" * 50)
    
    migrator = DatabaseMigrator()
    
    # Check if databases exist
    if not Path(migrator.main_db).exists():
        print(f"❌ Main database not found: {migrator.main_db}")
        return
    
    if not Path(migrator.skill_tree_db).exists():
        print(f"❌ Skill tree database not found: {migrator.skill_tree_db}")
        return
    
    # Confirm migration
    print(f"📋 This will migrate skill tree data from {migrator.skill_tree_db}")
    print(f"    to {migrator.main_db}")
    print()
    response = input("🤔 Continue with migration? (y/N): ").lower().strip()
    
    if response not in ['y', 'yes']:
        print("❌ Migration cancelled")
        return
    
    # Run migration
    success = migrator.run_full_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("✅ Main database now has skill tree functionality")
        print("🚀 You can now use the production server")
    else:
        print("\n❌ Migration failed - check logs for details")

if __name__ == "__main__":
    main()

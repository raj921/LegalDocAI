#!/usr/bin/env python
"""
Database migration script to add new columns for V2 template format.

This script safely adds the new columns (similarity_tags, body_md, example) 
to existing database tables without affecting existing data.
"""

import sqlite3
import sys
import os

DATABASE_PATH = "./legal_templates.db"

def migrate_database():
    """Add new columns to support V2 template format."""
    
    if not os.path.exists(DATABASE_PATH):
        print(f"✓ Database not found at {DATABASE_PATH}")
        print("✓ New database will be created with correct schema on first run")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Database Migration - V2 Template Format")
    print("=" * 60)
    
    migrations = []
    
    # Check and add similarity_tags to templates table
    try:
        cursor.execute("SELECT similarity_tags FROM templates LIMIT 1")
        print("✓ templates.similarity_tags already exists")
    except sqlite3.OperationalError:
        migrations.append(("templates", "similarity_tags", "TEXT"))
        print("→ Will add templates.similarity_tags column")
    
    # Check and add body_md to templates table
    try:
        cursor.execute("SELECT body_md FROM templates LIMIT 1")
        print("✓ templates.body_md already exists")
    except sqlite3.OperationalError:
        migrations.append(("templates", "body_md", "TEXT"))
        print("→ Will add templates.body_md column")
    
    # Check and add example to variables table
    try:
        cursor.execute("SELECT example FROM variables LIMIT 1")
        print("✓ variables.example already exists")
    except sqlite3.OperationalError:
        migrations.append(("variables", "example", "VARCHAR"))
        print("→ Will add variables.example column")
    
    # Execute migrations
    if migrations:
        print("\nApplying migrations...")
        for table, column, col_type in migrations:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                print(f"✓ Added {table}.{column}")
            except Exception as e:
                print(f"✗ Error adding {table}.{column}: {e}")
                conn.rollback()
                return False
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
    else:
        print("\n✓ Database already up to date - no migrations needed")
    
    # Show table info
    print("\n" + "=" * 60)
    print("Current Database Schema")
    print("=" * 60)
    
    cursor.execute("PRAGMA table_info(templates)")
    print("\nTemplates table:")
    for col in cursor.fetchall():
        print(f"  - {col[1]} ({col[2]})")
    
    cursor.execute("PRAGMA table_info(variables)")
    print("\nVariables table:")
    for col in cursor.fetchall():
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    return True

if __name__ == "__main__":
    try:
        success = migrate_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

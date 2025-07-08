#!/usr/bin/env python3
"""
Script per inizializzare il database
"""
import os
import sys
import logging

# Aggiungi il path per importare l'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import create_tables
from app.db.models import Base
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inizializza il database creando tutte le tabelle"""
    try:
        logger.info(f"Connecting to database: {settings.DATABASE_URL.split('@')[1]}")
        create_tables()
        logger.info("✅ Database initialized successfully!")
        
        # Stampa il riepilogo delle tabelle create
        logger.info("Tables created:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()

import asyncio
import logging
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.models.safety_event import SafetyEvent
from app.models.evidence import Evidence
from app.models.alert import Alert
from app.config import settings

logger = logging.getLogger("forgeguard.pruner")

async def auto_pruner_loop(session_maker):
    """
    Background loop that wakes up every 24 hours and cleans up old data.
    """
    await asyncio.sleep(10) # Initial wait
    
    while True:
        try:
            logger.info("Running Auto-Pruner cleanup job...")
            # We prune records older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            with session_maker() as db:
                # 1. Delete physical evidence files
                old_evidence = db.query(Evidence).filter(Evidence.created_at < cutoff_date).all()
                for ev in old_evidence:
                    if ev.image_path and ev.image_path.startswith("/uploads/evidence/"):
                        # Extract filename
                        filename = os.path.basename(ev.image_path)
                        filepath = os.path.join(settings.UPLOADS_DIR, "evidence", filename)
                        if os.path.exists(filepath):
                            try:
                                os.remove(filepath)
                                logger.info(f"Deleted old evidence file: {filepath}")
                            except Exception as e:
                                logger.error(f"Failed to delete file {filepath}: {e}")
                
                # 2. Delete database rows
                # Evidence
                deleted_ev = db.query(Evidence).filter(Evidence.created_at < cutoff_date).delete()
                # Safety Events
                deleted_se = db.query(SafetyEvent).filter(SafetyEvent.timestamp < cutoff_date).delete()
                # Alerts
                deleted_al = db.query(Alert).filter(Alert.timestamp < cutoff_date).delete()
                
                db.commit()
                logger.info(f"Auto-Pruner finished. Deleted {deleted_ev} evidence rows, {deleted_se} safety events, and {deleted_al} alerts older than {cutoff_date}.")
        
        except Exception as e:
            logger.error(f"Error in auto_pruner_loop: {e}")
            
        # Wait 24 hours before running again
        await asyncio.sleep(24 * 60 * 60)

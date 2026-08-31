import os
import zipfile
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.worker import Worker
from app.models.evidence import Evidence
from app.auth import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(tags=["export"])

@router.get("/api/workers/{worker_id}/export-evidence")
def export_worker_evidence(
    worker_id: int, 
    db: Session = Depends(get_db), 
    _: User = Depends(get_current_user)
):
    # 1. Validate worker exists
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    # 2. Get all evidence for this worker
    evidences = db.query(Evidence).filter(Evidence.worker_id == worker_id).all()
    if not evidences:
        raise HTTPException(status_code=404, detail="No evidence found for this worker")
        
    # 3. Create a ZIP file in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Create a CSV log file string
        log_content = "ID,Timestamp,Violation Type,Confidence,Camera ID\n"
        
        for ev in evidences:
            log_content += f"{ev.id},{ev.created_at},{ev.event_type},{ev.confidence}%,{ev.camera_id}\n"
            
            # If there's an image path, fetch the physical file and add it to the zip
            if ev.image_path and ev.image_path.startswith("/uploads/evidence/"):
                filename = os.path.basename(ev.image_path)
                filepath = os.path.join(settings.UPLOADS_DIR, "evidence", filename)
                
                if os.path.exists(filepath):
                    # Add file to zip under an 'images' folder
                    zip_file.write(filepath, arcname=f"images/{filename}")
                    
        # Add the text log to the zip
        zip_file.writestr("evidence_log.csv", log_content)

    # 4. Prepare response
    zip_buffer.seek(0)
    
    # Safe filename
    safe_name = "".join([c for c in worker.full_name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=evidence_{safe_name}.zip"
        }
    )

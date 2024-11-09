from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.scanners.web_scanner import WebScanner

router = APIRouter()
scanner = WebScanner()

class WebScanRequest(BaseModel):
    target_url: str
    options: Optional[dict] = {}

class WebScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

@router.post("/", response_model=WebScanResponse)
async def start_web_scan(request: WebScanRequest):
    try:
        scan_id = await scanner.start_scan(request.target_url, request.options)
        return {
            "scan_id": scan_id,
            "status": "started",
            "message": f"Scan started for {request.target_url}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scan_id}")
async def get_scan_status(scan_id: str):
    try:
        status = await scanner.get_scan_status(scan_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

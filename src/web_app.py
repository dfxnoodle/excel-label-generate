#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAPI web application for the label generator.
"""

import os
import io
import json
import tempfile
import numpy as np
import shutil
import time
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd

# Import our existing label generation modules
from simple_labels import load_data_from_excel, generate_labels, load_config


# Create a persistent upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# File cleanup configuration (in seconds)
FILE_MAX_AGE = 3600  # 1 hour = 3600 seconds
CLEANUP_INTERVAL = 300  # Run cleanup every 5 minutes

# Global storage for tracking uploaded files (just filenames, actual files on disk)
uploaded_files = set()

# Load existing uploaded files on startup
for file_path in UPLOAD_DIR.glob("*"):
    if file_path.is_file():
        uploaded_files.add(file_path.name)


def cleanup_old_uploads():
    """Remove uploaded files older than FILE_MAX_AGE seconds."""
    try:
        current_time = time.time()
        cleaned_count = 0
        
        for file_path in UPLOAD_DIR.glob("*"):
            # Skip .gitkeep and directories
            if file_path.name == ".gitkeep" or not file_path.is_file():
                continue
            
            # Check file age
            file_age = current_time - file_path.stat().st_mtime
            
            if file_age > FILE_MAX_AGE:
                try:
                    file_path.unlink()
                    uploaded_files.discard(file_path.name)
                    cleaned_count += 1
                    print(f"Cleaned up old file: {file_path.name} (age: {file_age:.0f}s)")
                except Exception as e:
                    print(f"Error cleaning up {file_path.name}: {e}")
        
        if cleaned_count > 0:
            print(f"Cleanup complete: {cleaned_count} file(s) removed")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")


async def periodic_cleanup():
    """Background task to periodically clean up old files."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        cleanup_old_uploads()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print(f"Starting file cleanup service (max age: {FILE_MAX_AGE}s, interval: {CLEANUP_INTERVAL}s)")
    # Clean up any old files from previous runs
    cleanup_old_uploads()
    # Start periodic cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown
    print("Shutting down file cleanup service...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app with lifespan
app = FastAPI(
    title="Label Generator API",
    description="Web API for generating labels from Excel data",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


# Pydantic models for API requests
class LabelConfig(BaseModel):
    category_filter: Optional[str] = None
    category_exclude_filter: Optional[str] = None
    status_filter: Optional[str] = None
    status_exclude_filter: Optional[str] = None
    mail_zone_filter: Optional[str] = None
    filter_mode: Optional[str] = "OR"  # "OR" or "AND"
    publication_columns: Optional[List[str]] = None
    limit: Optional[int] = None
    start_index: int = 0
    batch_size: Optional[int] = None


class GenerateLabelsRequest(BaseModel):
    filename: str
    config: Optional[LabelConfig] = None


# Create a persistent upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# File cleanup configuration (in seconds)
FILE_MAX_AGE = 3600  # 1 hour = 3600 seconds
CLEANUP_INTERVAL = 300  # Run cleanup every 5 minutes

# Global storage for tracking uploaded files (just filenames, actual files on disk)
uploaded_files = set()

# Load existing uploaded files on startup
for file_path in UPLOAD_DIR.glob("*"):
    if file_path.is_file():
        uploaded_files.add(file_path.name)


def cleanup_old_uploads():
    """Remove uploaded files older than FILE_MAX_AGE seconds."""
    try:
        current_time = time.time()
        cleaned_count = 0
        
        for file_path in UPLOAD_DIR.glob("*"):
            # Skip .gitkeep and directories
            if file_path.name == ".gitkeep" or not file_path.is_file():
                continue
            
            # Check file age
            file_age = current_time - file_path.stat().st_mtime
            
            if file_age > FILE_MAX_AGE:
                try:
                    file_path.unlink()
                    uploaded_files.discard(file_path.name)
                    cleaned_count += 1
                    print(f"Cleaned up old file: {file_path.name} (age: {file_age:.0f}s)")
                except Exception as e:
                    print(f"Error cleaning up {file_path.name}: {e}")
        
        if cleaned_count > 0:
            print(f"Cleanup complete: {cleaned_count} file(s) removed")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")


async def periodic_cleanup():
    """Background task to periodically clean up old files."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        cleanup_old_uploads()


def clean_data_for_json(data):
    """Clean data to make it JSON serializable by replacing NaN values."""
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif pd.isna(data) or (isinstance(data, float) and (np.isnan(data) or np.isinf(data))):
        return ""
    else:
        return data


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon."""
    from fastapi.responses import FileResponse
    return FileResponse("icon/favicon.ico")


@app.get("/config-page", response_class=HTMLResponse)
async def config_page(request: Request):
    """Serve the configuration management page."""
    return templates.TemplateResponse("config.html", {"request": request})


@app.post("/upload")
async def upload_excel_file(file: UploadFile = File(...)):
    """Upload an Excel file for processing."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
    
    try:
        # Read file content
        content = await file.read()
        
        # Save file to disk
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Track uploaded file
        uploaded_files.add(file.filename)
        
        # Load and preview the data
        df = pd.read_excel(file_path)
        
        # Get sample data and clean it for JSON serialization
        sample_data = df.head(3).to_dict(orient='records')
        clean_sample_data = clean_data_for_json(sample_data)
        
        # Count only non-empty rows (rows that have at least one non-null value)
        non_empty_rows = df.dropna(how='all').shape[0]
        
        return {
            "message": f"File '{file.filename}' uploaded successfully",
            "filename": file.filename,
            "rows": non_empty_rows,
            "columns": list(df.columns[:10]),  # Show first 10 columns as preview
            "sample_data": clean_sample_data  # Show first 3 rows
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.get("/files")
async def list_uploaded_files():
    """List all uploaded files."""
    return {"files": list(uploaded_files)}


@app.post("/export-filtered")
async def export_filtered_excel(request: GenerateLabelsRequest, background_tasks: BackgroundTasks):
    """Export filtered Excel data based on the provided configuration."""
    filename = request.filename
    
    if filename not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found. Please upload the file first.")
    
    # Get the file path from disk
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        # File was tracked but doesn't exist on disk - remove from tracking
        uploaded_files.discard(filename)
        raise HTTPException(status_code=404, detail="File not found on disk. Please upload the file again.")
    
    try:
        # Load data with filters if provided
        config_dict = request.config.dict() if request.config else {}
        
        df = load_data_from_excel(
            str(file_path),
            category_filter=config_dict.get('category_filter'),
            category_exclude_filter=config_dict.get('category_exclude_filter'),
            status_filter=config_dict.get('status_filter'),
            status_exclude_filter=config_dict.get('status_exclude_filter'),
            mail_zone_filter=config_dict.get('mail_zone_filter'),
            publication_columns=config_dict.get('publication_columns'),
            filter_mode=config_dict.get('filter_mode', 'OR')
        )
        
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="No data found after applying filters")
        
        # Apply batch processing if specified
        if config_dict.get('batch_size'):
            start_idx = config_dict.get('start_index', 0)
            end_idx = start_idx + config_dict['batch_size']
            df = df.iloc[start_idx:end_idx]
        elif config_dict.get('limit'):
            df = df.head(config_dict['limit'])
        
        # Create temporary output file for filtered Excel
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as output_file:
            output_path = output_file.name
        
        # Export filtered data to Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        # Schedule cleanup of temp output file after response
        background_tasks.add_task(os.unlink, output_path)
        
        # Return the Excel file
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"filtered_{filename}"
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting filtered data: {str(e)}")


@app.post("/generate")
async def generate_labels_endpoint(request: GenerateLabelsRequest, background_tasks: BackgroundTasks):
    """Generate labels from uploaded Excel data."""
    filename = request.filename
    
    if filename not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found. Please upload the file first.")
    
    # Get the file path from disk
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        # File was tracked but doesn't exist on disk - remove from tracking
        uploaded_files.discard(filename)
        raise HTTPException(status_code=404, detail="File not found on disk. Please upload the file again.")
    
    try:
        # Load data with filters if provided
        config_dict = request.config.dict() if request.config else {}
        
        df = load_data_from_excel(
            str(file_path),
            category_filter=config_dict.get('category_filter'),
            category_exclude_filter=config_dict.get('category_exclude_filter'),
            status_filter=config_dict.get('status_filter'),
            status_exclude_filter=config_dict.get('status_exclude_filter'),
            mail_zone_filter=config_dict.get('mail_zone_filter'),
            publication_columns=config_dict.get('publication_columns'),
            filter_mode=config_dict.get('filter_mode', 'OR')
        )
        
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="No data found or data could not be loaded")
        
        # Apply batch processing if specified
        if config_dict.get('batch_size'):
            start_idx = config_dict.get('start_index', 0)
            end_idx = start_idx + config_dict['batch_size']
            df = df.iloc[start_idx:end_idx]
        elif config_dict.get('limit'):
            df = df.head(config_dict['limit'])
        
        # Convert to records
        records = df.to_dict(orient='records')
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
            output_path = output_file.name
        
        # Load label configuration
        config_path = "config/label_config.json"
        
        # Prepare config overrides for publication codes display
        temp_config_overrides = {}
        
        # If publication_columns are specified, use them for display on labels
        if config_dict.get('publication_columns'):
            # The publication_columns from the request are the same as what should be displayed
            # For example, if filtering by ["BE"], display "BE" codes on labels
            temp_config_overrides['display_publication_codes_on_label'] = config_dict['publication_columns']
        
        # Generate labels with config overrides
        generate_labels(records, output_path, config_file=config_path, temp_config_overrides=temp_config_overrides)
        
        # Check if file was created successfully
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to generate labels")
        
        # Schedule cleanup of temp output file after response
        background_tasks.add_task(os.unlink, output_path)
        
        # Return the PDF file
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename=f"labels_{filename.split('.')[0]}.pdf"
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating labels: {str(e)}")


@app.get("/config")
async def get_config():
    """Get the current label configuration."""
    try:
        config_path = "config/label_config.json"
        config = load_config(config_path)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")


@app.post("/config")
async def update_config(config_data: dict):
    """Update the label configuration."""
    try:
        config_path = "config/label_config.json"
        
        # Load existing config
        config_path = "config/label_config.json"
        existing_config = load_config(config_path)
        
        # Update with new values
        existing_config.update(config_data)
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=4, ensure_ascii=False)
        
        return {"message": "Configuration updated successfully", "config": existing_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")


@app.post("/config/reset")
async def reset_config():
    """Reset configuration to defaults."""
    try:
        # Load default configuration (passing None loads defaults)
        default_config = load_config(None)
        
        # Save default config to file
        config_path = "config/label_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        return {"message": "Configuration reset to defaults successfully", "config": default_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting configuration: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Label Generator API is running"}


@app.get("/cleanup/status")
async def cleanup_status():
    """Get status of uploaded files and cleanup configuration."""
    try:
        current_time = time.time()
        files_info = []
        
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file() and file_path.name != ".gitkeep":
                age = current_time - file_path.stat().st_mtime
                size = file_path.stat().st_size
                will_be_deleted = age > FILE_MAX_AGE
                time_until_deletion = max(0, FILE_MAX_AGE - age)
                
                files_info.append({
                    "filename": file_path.name,
                    "age_seconds": int(age),
                    "age_formatted": f"{age/3600:.1f} hours" if age >= 3600 else f"{age/60:.1f} minutes",
                    "size_bytes": size,
                    "size_formatted": f"{size/1024:.1f} KB" if size >= 1024 else f"{size} bytes",
                    "will_be_deleted": will_be_deleted,
                    "time_until_deletion": int(time_until_deletion) if not will_be_deleted else 0,
                    "time_until_deletion_formatted": f"{time_until_deletion/60:.1f} minutes" if time_until_deletion < 3600 else f"{time_until_deletion/3600:.1f} hours"
                })
        
        return {
            "config": {
                "max_file_age_seconds": FILE_MAX_AGE,
                "max_file_age_formatted": f"{FILE_MAX_AGE/3600:.1f} hours",
                "cleanup_interval_seconds": CLEANUP_INTERVAL,
                "cleanup_interval_formatted": f"{CLEANUP_INTERVAL/60:.1f} minutes"
            },
            "files": files_info,
            "total_files": len(files_info),
            "files_to_be_deleted": sum(1 for f in files_info if f["will_be_deleted"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cleanup status: {str(e)}")


@app.post("/cleanup/run")
async def run_cleanup_now():
    """Manually trigger file cleanup."""
    try:
        current_time = time.time()
        cleaned_files = []
        
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.name == ".gitkeep" or not file_path.is_file():
                continue
            
            file_age = current_time - file_path.stat().st_mtime
            
            if file_age > FILE_MAX_AGE:
                try:
                    file_path.unlink()
                    uploaded_files.discard(file_path.name)
                    cleaned_files.append({
                        "filename": file_path.name,
                        "age_seconds": int(file_age)
                    })
                except Exception as e:
                    print(f"Error cleaning up {file_path.name}: {e}")
        
        return {
            "message": f"Cleanup completed: {len(cleaned_files)} file(s) removed",
            "cleaned_files": cleaned_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running cleanup: {str(e)}")


# Note: When running directly via python src/web_app.py, this will use default settings.
# For flexible port configuration, use: python run_web.py --port <PORT>
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}...")
    print(f"For flexible port configuration, use: python run_web.py --port <PORT>")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
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
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd

# Import our existing label generation modules
from simple_labels import load_data_from_excel, generate_labels, load_config


# Create FastAPI app
app = FastAPI(
    title="Label Generator API",
    description="Web API for generating labels from Excel data",
    version="1.0.0"
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


# Global storage for uploaded files (in production, use proper storage)
uploaded_files = {}


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
        
        # Store file content in memory (in production, save to disk or cloud storage)
        uploaded_files[file.filename] = content
        
        # Load and preview the data
        df = pd.read_excel(io.BytesIO(content))
        
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
    return {"files": list(uploaded_files.keys())}


@app.post("/export-filtered")
async def export_filtered_excel(request: GenerateLabelsRequest, background_tasks: BackgroundTasks):
    """Export filtered Excel data based on the provided configuration."""
    filename = request.filename
    
    if filename not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found. Please upload the file first.")
    
    try:
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(uploaded_files[filename])
            temp_file_path = temp_file.name
        
        try:
            # Load data with filters if provided
            config_dict = request.config.dict() if request.config else {}
            
            df = load_data_from_excel(
                temp_file_path,
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
            
            # Schedule cleanup of temp files after response
            background_tasks.add_task(os.unlink, output_path)
            background_tasks.add_task(os.unlink, temp_file_path)
            
            # Return the Excel file
            return FileResponse(
                output_path,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename=f"filtered_{filename}"
            )
            
        except Exception as inner_e:
            # Clean up temporary input file on error
            try:
                os.unlink(temp_file_path)
            except:
                pass
            raise inner_e
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting filtered data: {str(e)}")


@app.post("/generate")
async def generate_labels_endpoint(request: GenerateLabelsRequest, background_tasks: BackgroundTasks):
    """Generate labels from uploaded Excel data."""
    filename = request.filename
    
    if filename not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found. Please upload the file first.")
    
    try:
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(uploaded_files[filename])
            temp_file_path = temp_file.name
        
        try:
            # Load data with filters if provided
            config_dict = request.config.dict() if request.config else {}
            
            df = load_data_from_excel(
                temp_file_path,
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
            
            # Schedule cleanup of temp files after response
            background_tasks.add_task(os.unlink, output_path)
            background_tasks.add_task(os.unlink, temp_file_path)
            
            # Return the PDF file
            return FileResponse(
                output_path,
                media_type='application/pdf',
                filename=f"labels_{filename.split('.')[0]}.pdf"
            )
            
        except Exception as inner_e:
            # Clean up temporary input file on error
            try:
                os.unlink(temp_file_path)
            except:
                pass
            raise inner_e
            
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


# Note: When running directly via python src/web_app.py, this will use default settings.
# For flexible port configuration, use: python run_web.py --port <PORT>
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}...")
    print(f"For flexible port configuration, use: python run_web.py --port <PORT>")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
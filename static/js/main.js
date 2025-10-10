// JavaScript for the Label Generator web interface

let uploadedFileName = null;

document.addEventListener('DOMContentLoaded', function() {
    // Handle file upload
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    
    // Handle filtered Excel export
    document.getElementById('exportBtn').addEventListener('click', handleExportFiltered);
    
    // Handle label generation
    document.getElementById('generateBtn').addEventListener('click', handleGenerateLabels);
    
    // Setup dropdown handlers
    setupDropdownHandlers();
    
    // Setup filter mode toggle handlers
    setupFilterModeToggle();
});

function setupFilterModeToggle() {
    const orRadio = document.getElementById('filterModeOr');
    const andRadio = document.getElementById('filterModeAnd');
    const orDesc = document.getElementById('orModeDesc');
    const andDesc = document.getElementById('andModeDesc');
    
    if (orRadio && andRadio) {
        orRadio.addEventListener('change', function() {
            if (this.checked) {
                orDesc.style.display = '';
                andDesc.style.display = 'none';
            }
        });
        
        andRadio.addEventListener('change', function() {
            if (this.checked) {
                orDesc.style.display = 'none';
                andDesc.style.display = '';
            }
        });
    }
}

function setupDropdownHandlers() {
    // Category filter dropdown
    const categoryDropdown = document.getElementById('categoryDropdown');
    const categoryInput = document.getElementById('categoryFilter');
    const clearCategoryBtn = document.getElementById('clearCategoryBtn');
    
    categoryDropdown.addEventListener('change', function() {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        categoryInput.value = selected.join(',');
    });
    
    clearCategoryBtn.addEventListener('click', function() {
        categoryDropdown.selectedIndex = -1;
        categoryInput.value = '';
    });
    
    // Category exclude dropdown
    const categoryExcludeDropdown = document.getElementById('categoryExcludeDropdown');
    const categoryExcludeInput = document.getElementById('categoryExcludeFilter');
    const clearCategoryExcludeBtn = document.getElementById('clearCategoryExcludeBtn');
    
    categoryExcludeDropdown.addEventListener('change', function() {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        categoryExcludeInput.value = selected.join(',');
    });
    
    clearCategoryExcludeBtn.addEventListener('click', function() {
        categoryExcludeDropdown.selectedIndex = -1;
        categoryExcludeInput.value = '';
    });
    
    // Status filter dropdown
    const statusDropdown = document.getElementById('statusDropdown');
    const statusInput = document.getElementById('statusFilter');
    const clearStatusBtn = document.getElementById('clearStatusBtn');
    
    statusDropdown.addEventListener('change', function() {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        statusInput.value = selected.join(',');
    });
    
    clearStatusBtn.addEventListener('click', function() {
        statusDropdown.selectedIndex = -1;
        statusInput.value = '';
    });
    
    // Status exclude dropdown
    const statusExcludeDropdown = document.getElementById('statusExcludeDropdown');
    const statusExcludeInput = document.getElementById('statusExcludeFilter');
    const clearStatusExcludeBtn = document.getElementById('clearStatusExcludeBtn');
    
    statusExcludeDropdown.addEventListener('change', function() {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        statusExcludeInput.value = selected.join(',');
    });
    
    clearStatusExcludeBtn.addEventListener('click', function() {
        statusExcludeDropdown.selectedIndex = -1;
        statusExcludeInput.value = '';
    });
    
    // Mail zone dropdown
    const mailZoneDropdown = document.getElementById('mailZoneDropdown');
    const mailZoneInput = document.getElementById('mailZoneFilter');
    const clearMailZoneBtn = document.getElementById('clearMailZoneBtn');
    
    mailZoneDropdown.addEventListener('change', function() {
        const selected = Array.from(this.selectedOptions).map(opt => opt.value);
        mailZoneInput.value = selected.join(',');
    });
    
    clearMailZoneBtn.addEventListener('click', function() {
        mailZoneDropdown.selectedIndex = -1;
        mailZoneInput.value = '';
    });
}

async function handleFileUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('excelFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('uploadResult', 'Please select a file to upload.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading(true);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            uploadedFileName = result.filename;
            showUploadSuccess(result);
            showConfigSection();
            showDataPreview(result.sample_data, result.columns);
            showExportSection();
            showGenerateSection();
        } else {
            showError('uploadResult', result.detail || 'Upload failed');
        }
    } catch (error) {
        showError('uploadResult', 'Network error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function handleExportFiltered() {
    if (!uploadedFileName) {
        showError('exportResult', 'Please upload a file first.');
        return;
    }
    
    const config = getConfigFromForm();
    
    const requestData = {
        filename: uploadedFileName,
        config: config
    };
    
    // Show export button loading state
    const exportBtn = document.getElementById('exportBtn');
    const exportBtnText = exportBtn.querySelector('.export-btn-text');
    const exportBtnLoading = exportBtn.querySelector('.export-btn-loading');
    
    exportBtn.disabled = true;
    exportBtnText.style.display = 'none';
    exportBtnLoading.style.display = 'inline';
    
    showLoading(true);
    
    try {
        const response = await fetch('/export-filtered', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            // Handle file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `filtered_${uploadedFileName}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showSuccess('exportResult', 'Filtered Excel file exported successfully! Download should start automatically.');
        } else {
            const errorData = await response.json();
            showError('exportResult', errorData.detail || 'Export failed');
        }
    } catch (error) {
        showError('exportResult', 'Network error: ' + error.message);
    } finally {
        // Reset export button state
        exportBtn.disabled = false;
        exportBtnText.style.display = 'inline';
        exportBtnLoading.style.display = 'none';
        showLoading(false);
    }
}

async function handleGenerateLabels() {
    if (!uploadedFileName) {
        showError('generateResult', 'Please upload a file first.');
        return;
    }
    
    const config = getConfigFromForm();
    
    const requestData = {
        filename: uploadedFileName,
        config: config
    };
    
    showLoading(true);
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            // Handle file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `labels_${uploadedFileName.split('.')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showSuccess('generateResult', 'Labels generated successfully! Download should start automatically.');
        } else {
            const errorData = await response.json();
            showError('generateResult', errorData.detail || 'Generation failed');
        }
    } catch (error) {
        showError('generateResult', 'Network error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function getConfigFromForm() {
    const config = {};
    
    const categoryFilter = document.getElementById('categoryFilter').value.trim();
    if (categoryFilter) config.category_filter = categoryFilter;
    
    const categoryExcludeFilter = document.getElementById('categoryExcludeFilter').value.trim();
    if (categoryExcludeFilter) config.category_exclude_filter = categoryExcludeFilter;
    
    const statusFilter = document.getElementById('statusFilter').value.trim();
    if (statusFilter) config.status_filter = statusFilter;
    
    const statusExcludeFilter = document.getElementById('statusExcludeFilter').value.trim();
    if (statusExcludeFilter) config.status_exclude_filter = statusExcludeFilter;
    
    const mailZoneFilter = document.getElementById('mailZoneFilter').value.trim();
    if (mailZoneFilter) config.mail_zone_filter = mailZoneFilter;
    
    // Get filter mode (OR or AND)
    const filterMode = document.querySelector('input[name="filterMode"]:checked')?.value || 'OR';
    config.filter_mode = filterMode;
    
    // Get selected publication columns
    const publicationColumns = [];
    if (document.getElementById('pubBE').checked) publicationColumns.push('BE');
    if (document.getElementById('pubBC').checked) publicationColumns.push('BC');
    if (document.getElementById('pubAR').checked) publicationColumns.push('AR');
    if (publicationColumns.length > 0) config.publication_columns = publicationColumns;
    
    const limitNumber = document.getElementById('limitNumber').value;
    if (limitNumber) config.limit = parseInt(limitNumber);
    
    const batchSize = document.getElementById('batchSize').value;
    if (batchSize) config.batch_size = parseInt(batchSize);
    
    const startIndex = document.getElementById('startIndex').value;
    if (startIndex) config.start_index = parseInt(startIndex);
    
    return Object.keys(config).length > 0 ? config : null;
}

function showUploadSuccess(result) {
    const resultDiv = document.getElementById('uploadResult');
    resultDiv.innerHTML = `
        <div class="file-info fade-in">
            <h5>✓ File Uploaded Successfully</h5>
            <p><strong>Filename:</strong> ${result.filename}</p>
            <p><strong>Total Rows:</strong> ${result.rows}</p>
            <p><strong>Columns:</strong> ${result.columns.join(', ')}</p>
        </div>
    `;
}

function showConfigSection() {
    document.getElementById('configSection').style.display = 'block';
}

function showDataPreview(sampleData, columns) {
    const previewDiv = document.getElementById('dataPreview');
    
    if (sampleData && sampleData.length > 0) {
        let tableHtml = `
            <div class="preview-table">
                <table class="table table-striped table-sm">
                    <thead>
                        <tr>
        `;
        
        // Show only first 8 columns for preview
        const previewColumns = columns.slice(0, 8);
        previewColumns.forEach(col => {
            tableHtml += `<th>${col}</th>`;
        });
        
        if (columns.length > 8) {
            tableHtml += '<th>...</th>';
        }
        
        tableHtml += '</tr></thead><tbody>';
        
        sampleData.forEach(row => {
            tableHtml += '<tr>';
            previewColumns.forEach(col => {
                const value = row[col] || '';
                tableHtml += `<td>${String(value).substring(0, 50)}${String(value).length > 50 ? '...' : ''}</td>`;
            });
            if (columns.length > 8) {
                tableHtml += '<td>...</td>';
            }
            tableHtml += '</tr>';
        });
        
        tableHtml += '</tbody></table></div>';
        
        previewDiv.innerHTML = tableHtml;
        document.getElementById('previewSection').style.display = 'block';
    }
}

function showExportSection() {
    document.getElementById('exportSection').style.display = 'block';
}

function showGenerateSection() {
    document.getElementById('generateSection').style.display = 'block';
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="error-message fade-in">${message}</div>`;
}

function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="success-message fade-in">${message}</div>`;
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    spinner.style.display = show ? 'block' : 'none';
}
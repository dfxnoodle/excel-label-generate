// JavaScript for the Configuration page

let currentConfig = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load current configuration on page load
    loadConfiguration();
    
    // Setup event listeners
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfiguration);
    document.getElementById('loadConfigBtn').addEventListener('click', loadConfiguration);
    document.getElementById('resetConfigBtn').addEventListener('click', resetConfiguration);
});

async function loadConfiguration() {
    showLoading(true);
    
    try {
        const response = await fetch('/config');
        if (response.ok) {
            currentConfig = await response.json();
            populateConfigForm(currentConfig);
            showSuccess('configResult', 'Configuration loaded successfully');
        } else {
            const errorData = await response.json();
            showError('configResult', errorData.detail || 'Failed to load configuration');
        }
    } catch (error) {
        showError('configResult', 'Network error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function populateConfigForm(config) {
    // Page Layout
    document.getElementById('pageSize').value = config.page_size || 'A4';
    document.getElementById('columns').value = config.columns || 2;
    document.getElementById('rows').value = config.rows || 8;
    document.getElementById('labelWidth').value = config.label_width || 95;
    document.getElementById('labelHeight').value = config.label_height || 30;
    document.getElementById('showBorder').value = config.show_border ? 'true' : 'false';
    document.getElementById('borderWidth').value = config.border_width || 0.1;
    document.getElementById('marginTop').value = config.margin_top || 5;
    document.getElementById('marginBottom').value = config.margin_bottom || 5;
    document.getElementById('marginLeft').value = config.margin_left || 5;
    document.getElementById('marginRight').value = config.margin_right || 5;
    
    // Fonts
    const fonts = config.fonts || {};
    
    if (fonts.title) {
        document.getElementById('titleFontName').value = fonts.title.name || 'Helvetica-Bold';
        document.getElementById('titleFontSize').value = fonts.title.size || 10;
    }
    
    if (fonts.body) {
        document.getElementById('bodyFontName').value = fonts.body.name || 'Helvetica';
        document.getElementById('bodyFontSize').value = fonts.body.size || 9;
    }
    
    if (fonts.cjk) {
        document.getElementById('cjkFontName').value = fonts.cjk.name || 'SimSun';
        document.getElementById('cjkFontSize').value = fonts.cjk.size || 9;
        document.getElementById('cjkFontFile').value = fonts.cjk.file || 'SimSun.ttf';
    }
    
    if (fonts.annotation_font) {
        document.getElementById('annotationFontName').value = fonts.annotation_font.name || 'Helvetica-Oblique';
        document.getElementById('annotationFontSize').value = fonts.annotation_font.size || 8;
    }
    
    if (fonts.publication) {
        document.getElementById('publicationFontName').value = fonts.publication.name || 'Helvetica-Bold';
        document.getElementById('publicationFontSize').value = fonts.publication.size || 14;
    }
    
    // Colors
    const colors = config.colors || {};
    document.getElementById('textColor').value = colors.text || '#000000';
    document.getElementById('titleColor').value = colors.title || '#000000';
    document.getElementById('bodyColor').value = colors.body || '#000000';
    document.getElementById('borderColor').value = colors.border || '#000000';
    
    // Custom text
    document.getElementById('bulletinText').value = config.bulletin_text || 'Bulletin';
    document.getElementById('bulletinNumber').value = config.bulletin_number_text || 'No.X-YYYY';
    document.getElementById('customRightPanel').value = config.custom_right_panel_text || '';
    
    // Field checkboxes
    populateFieldCheckboxes(config);
}

function populateFieldCheckboxes(config) {
    const fieldContainer = document.getElementById('fieldCheckboxes');
    const allFields = config.all_fields_info || [];
    const selectedFields = config.display_selected_fields_on_label || [];
    
    fieldContainer.innerHTML = '';
    
    allFields.forEach(field => {
        const isChecked = selectedFields.includes(field.key);
        const checkboxHtml = `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="field_${field.key}" value="${field.key}" ${isChecked ? 'checked' : ''}>
                <label class="form-check-label" for="field_${field.key}">
                    ${field.label} (${field.key})
                </label>
            </div>
        `;
        fieldContainer.insertAdjacentHTML('beforeend', checkboxHtml);
    });
}

async function saveConfiguration() {
    if (!currentConfig) {
        showError('configResult', 'No configuration loaded');
        return;
    }
    
    const updatedConfig = collectConfigFromForm();
    
    showLoading(true);
    
    try {
        const response = await fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedConfig)
        });
        
        if (response.ok) {
            const result = await response.json();
            currentConfig = result.config;
            showSuccess('configResult', 'Configuration saved successfully!');
        } else {
            const errorData = await response.json();
            showError('configResult', errorData.detail || 'Failed to save configuration');
        }
    } catch (error) {
        showError('configResult', 'Network error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function collectConfigFromForm() {
    const config = {...currentConfig};
    
    // Page Layout
    config.page_size = document.getElementById('pageSize').value;
    config.columns = parseInt(document.getElementById('columns').value);
    config.rows = parseInt(document.getElementById('rows').value);
    config.label_width = parseFloat(document.getElementById('labelWidth').value);
    config.label_height = parseFloat(document.getElementById('labelHeight').value);
    config.show_border = document.getElementById('showBorder').value === 'true';
    config.border_width = parseFloat(document.getElementById('borderWidth').value);
    config.margin_top = parseFloat(document.getElementById('marginTop').value);
    config.margin_bottom = parseFloat(document.getElementById('marginBottom').value);
    config.margin_left = parseFloat(document.getElementById('marginLeft').value);
    config.margin_right = parseFloat(document.getElementById('marginRight').value);
    
    // Fonts
    config.fonts = config.fonts || {};
    
    config.fonts.title = {
        name: document.getElementById('titleFontName').value,
        size: parseInt(document.getElementById('titleFontSize').value)
    };
    
    config.fonts.body = {
        name: document.getElementById('bodyFontName').value,
        size: parseInt(document.getElementById('bodyFontSize').value)
    };
    
    config.fonts.cjk = {
        name: document.getElementById('cjkFontName').value,
        size: parseInt(document.getElementById('cjkFontSize').value),
        file: document.getElementById('cjkFontFile').value
    };
    
    config.fonts.annotation_font = {
        name: document.getElementById('annotationFontName').value,
        size: parseInt(document.getElementById('annotationFontSize').value)
    };
    
    config.fonts.publication = {
        name: document.getElementById('publicationFontName').value,
        size: parseInt(document.getElementById('publicationFontSize').value)
    };
    
    // Colors
    config.colors = config.colors || {};
    config.colors.text = document.getElementById('textColor').value;
    config.colors.title = document.getElementById('titleColor').value;
    config.colors.body = document.getElementById('bodyColor').value;
    config.colors.border = document.getElementById('borderColor').value;
    
    // Custom text
    config.bulletin_text = document.getElementById('bulletinText').value;
    config.bulletin_number_text = document.getElementById('bulletinNumber').value;
    config.custom_right_panel_text = document.getElementById('customRightPanel').value;
    
    // Selected fields
    const selectedFields = [];
    const checkboxes = document.querySelectorAll('#fieldCheckboxes input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        selectedFields.push(checkbox.value);
    });
    config.display_selected_fields_on_label = selectedFields;
    
    return config;
}

async function resetConfiguration() {
    if (!confirm('Are you sure you want to reset the configuration to defaults? This will overwrite all current settings.')) {
        return;
    }
    
    showLoading(true);
    
    try {
        // Load default configuration by sending an empty config object
        const response = await fetch('/config/reset', {
            method: 'POST'
        });
        
        if (response.ok) {
            await loadConfiguration();
            showSuccess('configResult', 'Configuration reset to defaults successfully!');
        } else {
            const errorData = await response.json();
            showError('configResult', errorData.detail || 'Failed to reset configuration');
        }
    } catch (error) {
        showError('configResult', 'Network error: ' + error.message);
    } finally {
        showLoading(false);
    }
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
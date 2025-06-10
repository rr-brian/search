// Grid configuration
const gridOptions = {
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true
    },
    columnDefs: [
        { 
            field: 'metadata_storage_name',
            headerName: 'Filename',
            flex: 1,
            minWidth: 200,
            valueGetter: params => {
                console.log('Grid row data:', params.data);
                if (!params.data) {
                    console.log('No data in params');
                    return '';
                }
                
                // Try different fields for filename
                const fields = ['metadata_storage_name', 'filename', 'filepath'];
                for (const field of fields) {
                    const value = params.data[field];
                    console.log(`Checking ${field}:`, value);
                    if (value) {
                        const parts = value.split(/[\/\\]/);
                        const filename = parts[parts.length - 1];
                        console.log(`Using ${field} for filename:`, filename);
                        return filename;
                    }
                }
                
                console.log('No filename found in any field');
                return '';
            }
        },
        { 
            headerName: 'Content',
            field: 'content',
            flex: 2,
            minWidth: 400,
            wrapText: true,
            autoHeight: true,
            cellRenderer: params => {
                if (!params.value) return '';
                
                const content = params.value;
                const preview = content.substring(0, 200);
                const needsExpansion = content.length > 200;
                
                // Encode content to base64, handling non-Latin1 characters
                const encodedContent = btoa(unescape(encodeURIComponent(content)));
                
                // Create preview HTML with proper escaping
                const previewHtml = `<div class="content-preview" data-encoded-content="${encodedContent}">${escapeHtml(preview)}${needsExpansion ? '...' : ''}</div>`;
                
                if (needsExpansion) {
                    // Create button HTML
                    const buttonHtml = `<button class="btn btn-link btn-sm expand-btn" onclick="window.expandContent(this, '${encodedContent}')" style="padding: 0; margin-top: 5px;">Show More</button>`;
                    return `<div>${previewHtml}${buttonHtml}</div>`;
                }
                
                return `<div>${previewHtml}</div>`;
            }
        }
    ],
    rowData: [],
    domLayout: 'autoHeight',
    enableCellTextSelection: true,
    suppressScrollOnNewData: true,
    suppressMovableColumns: true,
    onRowDoubleClicked: params => {
        const contentCell = params.event.target.closest('.ag-cell');
        if (!contentCell) return;
        
        const contentPreview = contentCell.querySelector('.content-preview');
        if (!contentPreview) return;
        
        const encodedContent = contentPreview.dataset.encodedContent;
        if (!encodedContent) return;
        
        const btn = contentCell.querySelector('.expand-btn');
        if (btn) {
            window.expandContent(btn, encodedContent);
        }
    }
};

// Helper function for HTML escaping
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Function to expand/collapse content
function expandContent(btn, encodedContent) {
    const contentDiv = btn.previousElementSibling;
    // Decode base64 and handle non-Latin1 characters
    const content = decodeURIComponent(escape(atob(encodedContent)));
    
    if (btn.textContent === 'Show More') {
        contentDiv.innerHTML = escapeHtml(content);
        btn.textContent = 'Show Less';
    } else {
        contentDiv.innerHTML = escapeHtml(content.substring(0, 200)) + '...';
        btn.textContent = 'Show More';
    }
}

// Export for use in search.js
window.gridOptions = gridOptions;
window.expandContent = expandContent;

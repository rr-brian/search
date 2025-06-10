// Initialize search history and grid API
let searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
let gridApi;

// Update datalist with history
function updateSearchHistory() {
    const datalist = document.getElementById('searchHistory');
    datalist.innerHTML = searchHistory
        .map(query => `<option value="${query}">`)
        .join('');
}

// Clear search history
function clearHistory() {
    searchHistory = [];
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    updateSearchHistory();
}

// Add query to history
function addToHistory(query) {
    if (query && !searchHistory.includes(query)) {
        searchHistory.unshift(query);
        if (searchHistory.length > 10) {
            searchHistory.pop();
        }
        localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
        updateSearchHistory();
    }
}

// Function to perform search
async function testSearch() {
    const query = document.getElementById('searchInput').value.trim();
    const loading = document.getElementById('loading');
    
    if (!query) {
        showAlert('warning', 'Please enter a search query');
        return;
    }
    
    try {
        loading.style.display = 'block';
        addToHistory(query);
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data || !Array.isArray(data)) {
            throw new Error('Invalid response format from server');
        }
        
        // Debug log the data
        console.log('Search results:', data);
        if (data && data.length > 0) {
            console.log('First result fields:', Object.keys(data[0]));
            console.log('First result:', data[0]);
        }

        // Update grid data
        gridApi.setRowData(data);
        gridApi.sizeColumnsToFit();
        
        // Update summary if available
        const firstRow = data[0];
        if (firstRow && firstRow.summary) {
            const summaryDiv = document.getElementById('searchSummary');
            const summaryContent = document.getElementById('summaryContent');
            summaryContent.textContent = firstRow.summary;
            summaryDiv.style.display = 'block';
        } else {
            document.getElementById('searchSummary').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showAlert('danger', `Error: ${error.message}`);
    } finally {
        loading.style.display = 'none';
    }
}

// Function to show alerts
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    const existingAlert = container.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    container.insertBefore(alertDiv, document.getElementById('gridContainer'));
    setTimeout(() => alertDiv.remove(), 5000);
}

// Function to expand/collapse content
function expandContent(btn, encodedContent) {
    const contentDiv = btn.previousElementSibling;
    // Decode base64 and handle non-Latin1 characters
    const content = decodeURIComponent(escape(atob(encodedContent)));
    
    if (btn.textContent === 'Show More') {
        contentDiv.innerHTML = content;
        btn.textContent = 'Show Less';
    } else {
        contentDiv.innerHTML = content.substring(0, 200) + '...';
        btn.textContent = 'Show More';
    }
}

// Initialize the grid when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing grid...');
    const gridDiv = document.getElementById('gridContainer');
    const grid = new agGrid.Grid(gridDiv, window.gridOptions);
    gridApi = window.gridOptions.api;
    console.log('Grid initialized, API:', gridApi);
    if (gridApi) {
        gridApi.sizeColumnsToFit();
        console.log('Grid sized to fit');
    } else {
        console.error('Failed to initialize grid API');
    }
    
    // Initialize history display
    updateSearchHistory();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    const searchInput = document.getElementById('searchInput');
    
    // Focus search with '/'
    if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
    }
    
    // Handle up/down arrows for history
    if (document.activeElement === searchInput) {
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            e.preventDefault();
            const currentValue = searchInput.value;
            const currentIndex = searchHistory.indexOf(currentValue);
            let newIndex;
            
            if (e.key === 'ArrowUp') {
                newIndex = currentIndex === -1 ? 0 : (currentIndex + 1 >= searchHistory.length ? -1 : currentIndex + 1);
            } else {
                newIndex = currentIndex === -1 ? searchHistory.length - 1 : (currentIndex - 1 < 0 ? -1 : currentIndex - 1);
            }
            
            searchInput.value = newIndex === -1 ? '' : searchHistory[newIndex];
        }
    }
});

// Add enter key support
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        const query = this.value.trim();
        if (query) {
            addToHistory(query);
            testSearch();
        }
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    if (gridApi) {
        gridApi.sizeColumnsToFit();
    }
});

// Export for use in other files
window.testSearch = testSearch;
window.showAlert = showAlert;

// Admin panel functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add sorting functionality to table headers
    const tableHeaders = document.querySelectorAll('th');
    tableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const index = Array.from(header.parentElement.children).indexOf(header);
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.children[index].textContent.trim();
                const bValue = b.children[index].textContent.trim();
                return aValue.localeCompare(bValue);
            });
            
            // Toggle sort direction
            if (header.classList.contains('sort-asc')) {
                rows.reverse();
                header.classList.remove('sort-asc');
                header.classList.add('sort-desc');
            } else {
                header.classList.remove('sort-desc');
                header.classList.add('sort-asc');
            }
            
            // Clear other headers' sort classes
            tableHeaders.forEach(h => {
                if (h !== header) {
                    h.classList.remove('sort-asc', 'sort-desc');
                }
            });
            
            // Update table
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    });
    
    // Add search functionality
    const searchInput = document.getElementById('userSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#userTableBody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
}); 
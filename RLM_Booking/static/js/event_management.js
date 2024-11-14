document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('data-table');

    // Function to sort table by column index
    function sortTable(columnIndex, order) {
        const rows = Array.from(table.getElementsByTagName('tr'));

        rows.sort((a, b) => {
            const cellA = a.getElementsByTagName('td')[columnIndex].textContent.trim();
            const cellB = b.getElementsByTagName('td')[columnIndex].textContent.trim();

            // Handle date comparison for Times column
            if (columnIndex === 2) {
                return order === 'asc'
                    ? new Date(cellA) - new Date(cellB)
                    : new Date(cellB) - new Date(cellA);
            }

            // Handle string comparison for other columns
            return order === 'asc'
                ? cellA.localeCompare(cellB)
                : cellB.localeCompare(cellA);
        });

        // Reorder rows in the table body
        rows.forEach(row => table.appendChild(row));
    }

    // Attach event listeners to sort buttons
    document.querySelectorAll('.sort-btn').forEach(button => {
        button.addEventListener('click', function() {
            const columnIndex = parseInt(this.getAttribute('data-column'));
            const currentOrder = this.getAttribute('data-sort');

            // Toggle sort order
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            this.setAttribute('data-sort', newOrder);

            // Sort table
            sortTable(columnIndex, newOrder);
        });
    });
});
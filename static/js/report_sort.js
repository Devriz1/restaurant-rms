(function () {
    'use strict';

    const SORT_STATE_KEY = 'report_sort_state';

    function getSortKey(tableId) {
        return `${SORT_STATE_KEY}_${tableId}`;
    }

    function getSavedSort(tableId) {
        try {
            const raw = localStorage.getItem(getSortKey(tableId));
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    }

    function saveSort(tableId, column, direction) {
        try {
            localStorage.setItem(getSortKey(tableId), JSON.stringify({ column, direction }));
        } catch (e) {
            // ignore
        }
    }

    function sortTable(table, column, direction) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        const rows = Array.from(tbody.querySelectorAll('tr'));
        const headerIndex = Array.from(table.querySelectorAll('thead th')).findIndex(
            (th) => th.getAttribute('data-column') === column
        );

        if (headerIndex === -1) return;

        const isNumeric = (value) => {
            const cleaned = String(value).replace(/[^0-9.-]/g, '');
            return cleaned !== '' && !isNaN(cleaned);
        };

        const getCellValue = (row) => {
            const cell = row.querySelector(`td[data-column="${column}"]`);
            if (!cell) return '';
            return cell.textContent.trim();
        };

        rows.sort((a, b) => {
            const valA = getCellValue(a);
            const valB = getCellValue(b);

            let comparison = 0;

            if (isNumeric(valA) && isNumeric(valB)) {
                const numA = parseFloat(valA.replace(/[^0-9.-]/g, '')) || 0;
                const numB = parseFloat(valB.replace(/[0-9.,]/g, '')) || 0;
                comparison = numA - numB;
            } else {
                comparison = valA.localeCompare(valB, undefined, { numeric: true, sensitivity: 'base' });
            }

            return direction === 'desc' ? comparison * -1 : comparison;
        });

        rows.forEach((row) => tbody.appendChild(row));

        table.querySelectorAll('thead th').forEach((th) => {
            const icon = th.querySelector('.sort-icon');
            if (icon) icon.remove();

            if (th.getAttribute('data-column') === column) {
                const span = document.createElement('i');
                span.className = 'sort-icon bi ms-1 text-muted';
                span.classList.add(direction === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down');
                th.appendChild(span);
            }
        });
    }

    function init(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const saved = getSavedSort(tableId);
        if (saved) {
            sortTable(table, saved.column, saved.direction);
        }

        table.querySelectorAll('thead th.sortable-header').forEach((th) => {
            th.addEventListener('click', () => {
                const column = th.getAttribute('data-column');
                const currentDirection = th.getAttribute('data-sort') || 'asc';
                const nextDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                th.setAttribute('data-sort', nextDirection);
                sortTable(table, column, nextDirection);
                saveSort(tableId, column, nextDirection);
            });
        });
    }

    window.ReportSort = { init };
})();

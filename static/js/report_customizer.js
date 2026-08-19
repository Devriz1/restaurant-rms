(function () {
    'use strict';

    const STORAGE_KEY = 'report_customizer_state';

    function getStorageKey(tableId) {
        return `${STORAGE_KEY}_${tableId}`;
    }

    function getSavedState(tableId) {
        try {
            const raw = localStorage.getItem(getStorageKey(tableId));
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    }

    function saveState(tableId, state) {
        try {
            localStorage.setItem(getStorageKey(tableId), JSON.stringify(state));
        } catch (e) {
            // storage not available
        }
    }

    function openCustomizer() {
        const customizer = document.getElementById('reportCustomizer');
        if (!customizer) return;
        customizer.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeCustomizer() {
        const customizer = document.getElementById('reportCustomizer');
        if (!customizer) return;
        customizer.classList.remove('open');
        document.body.style.overflow = '';
    }

    function applyColumns(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const checkboxes = document.querySelectorAll('#columnList input[type="checkbox"]');
        const headers = table.querySelectorAll('thead th');
        const bodyRows = table.querySelectorAll('tbody tr');

        checkboxes.forEach((checkbox, index) => {
            const columnKey = checkbox.getAttribute('data-column');
            const isChecked = checkbox.checked;

            headers.forEach((th) => {
                if (th.getAttribute('data-column') === columnKey) {
                    th.style.display = isChecked ? '' : 'none';
                }
            });

            bodyRows.forEach((row) => {
                const cells = row.querySelectorAll('td');
                if (cells[index]) {
                    cells[index].style.display = isChecked ? '' : 'none';
                }
            });
        });

        saveState(tableId, Array.from(checkboxes).map((cb) => ({
            column: cb.getAttribute('data-column'),
            checked: cb.checked,
        })));
    }

    function resetColumns(tableId) {
        const checkboxes = document.querySelectorAll('#columnList input[type="checkbox"]');
        checkboxes.forEach((cb) => {
            cb.checked = true;
        });
        applyColumns(tableId);
    }

    function init(tableId) {
        const saved = getSavedState(tableId);
        if (saved) {
            const checkboxes = document.querySelectorAll('#columnList input[type="checkbox"]');
            checkboxes.forEach((cb) => {
                const entry = saved.find((s) => s.column === cb.getAttribute('data-column'));
                if (entry) {
                    cb.checked = entry.checked;
                }
            });
            applyColumns(tableId);
        }

        const openBtn = document.getElementById('openCustomizer');
        const closeBtn = document.getElementById('closeCustomizer');
        const resetBtn = document.getElementById('resetColumns');
        const applyBtn = document.getElementById('applyColumns');

        if (openBtn) {
            openBtn.addEventListener('click', openCustomizer);
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', closeCustomizer);
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => resetColumns(tableId));
        }

        if (applyBtn) {
            applyBtn.addEventListener('click', () => applyColumns(tableId));
        }

        const overlay = document.querySelector('.customizer-overlay');
        if (overlay) {
            overlay.addEventListener('click', closeCustomizer);
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeCustomizer();
            }
        });
    }

    window.ReportCustomizer = {
        init,
        applyColumns,
        resetColumns,
    };
})();

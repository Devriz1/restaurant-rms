(function () {
    'use strict';

    function init() {
        const searchInputs = document.querySelectorAll('#reportSearch');

        searchInputs.forEach((input) => {
            input.addEventListener('keyup', () => {
                const term = input.value.toLowerCase();
                const table = input.closest('.card')?.querySelector('table')
                    || input.closest('.report-table-card')?.querySelector('table')
                    || input.closest('.report-table')?.querySelector('table');

                if (!table) return;

                const rows = table.querySelectorAll('tbody tr');
                let visibleCount = 0;

                rows.forEach((row) => {
                    const text = row.textContent.toLowerCase();
                    const match = text.includes(term);
                    row.style.display = match ? '' : 'none';
                    if (match) visibleCount++;
                });

                const recordCount = table.closest('.card-body')?.querySelector('#recordCount');
                if (recordCount) {
                    recordCount.textContent = visibleCount;
                }
            });
        });

        const quickButtons = document.querySelectorAll('.quick-btn[data-range]');
        const rangeInput = document.getElementById('rangeInput');
        const filterForm = document.querySelector('.report-toolbar form');

        quickButtons.forEach((btn) => {
            btn.addEventListener('click', () => {
                if (!rangeInput || !filterForm) return;

                rangeInput.value = btn.getAttribute('data-range');

                quickButtons.forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');

                filterForm.submit();
            });
        });
    }

    window.ReportSearch = { init };
})();

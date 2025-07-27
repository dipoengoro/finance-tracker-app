document.addEventListener('DOMContentLoaded', function() {
    const exportBtn = document.getElementById('export-btn');

    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Mengunduh...
            `;
            exportBtn.classList.add('disabled');

            setTimeout(function() {
                exportBtn.innerHTML = 'Ekspor ke CSV';
                exportBtn.classList.remove('disabled');
            }, 2000);
        });
    }
});

function toggleItemEdit(itemId) {
    const viewRow = document.getElementById('item-view-' + itemId);
    const editRow = document.getElementById('item-edit-' + itemId);

    if (viewRow.style.display !== 'none') {
        viewRow.style.display = 'none';
        editRow.style.display = 'table-row';
    } else {
        viewRow.style.display = 'table-row';
        editRow.style.display = 'none';
    }
}
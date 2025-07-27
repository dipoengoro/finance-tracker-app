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
document.addEventListener("DOMContentLoaded", function () {
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function () {
            let checkboxes = document.querySelectorAll('input[name="selected_requests"]');
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
});

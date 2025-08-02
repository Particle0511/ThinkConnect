document.addEventListener('DOMContentLoaded', function () {

    // Initialize Bootstrap Tooltips
    const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Add confirmation dialog for delete actions
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const isConfirmed = confirm('Are you sure you want to delete this? This action cannot be undone.');
            if (!isConfirmed) {
                event.preventDefault();
            }
        });
    });

    // Theme Toggle Logic
    const themeCheckbox = document.getElementById('theme-checkbox');
    const currentTheme = localStorage.getItem('theme');

    // Set initial theme and checkbox state from localStorage
    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            themeCheckbox.checked = true;
        }
    }

    // Listen for changes on the checkbox to switch themes
    themeCheckbox.addEventListener('change', function() {
        if (this.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

});
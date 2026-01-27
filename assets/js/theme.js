// Theme Toggle Logic
// Uses localStorage to persist preference
// Defaults to 'dark'

(function() {
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // Update icon if it exists
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            const icon = theme === 'dark' ? '☀️' : '🌙';
            btn.textContent = icon;
            btn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
        }
    }

    // Initialize
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);

    // Expose toggle function
    window.toggleTheme = function() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
    };

    // Add button logic when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.onclick = window.toggleTheme;
            // Set initial icon state
            const current = document.documentElement.getAttribute('data-theme');
            btn.textContent = current === 'dark' ? '☀️' : '🌙';
        }
    });
})();

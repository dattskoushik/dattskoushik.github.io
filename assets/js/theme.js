// Theme Toggle Logic & Mobile Menu
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

    // DOM Ready
    document.addEventListener('DOMContentLoaded', () => {
        // Theme Toggle
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.onclick = window.toggleTheme;
            const current = document.documentElement.getAttribute('data-theme');
            themeBtn.textContent = current === 'dark' ? '☀️' : '🌙';
        }

        // Mobile Menu
        const menuBtn = document.querySelector('.mobile-menu-btn');
        const navLinks = document.querySelector('.nav-links');

        if (menuBtn && navLinks) {
            menuBtn.addEventListener('click', () => {
                const isExpanded = menuBtn.getAttribute('aria-expanded') === 'true';
                menuBtn.setAttribute('aria-expanded', !isExpanded);
                navLinks.classList.toggle('active');
                menuBtn.textContent = isExpanded ? '☰' : '✕';
            });
        }
    });
})();

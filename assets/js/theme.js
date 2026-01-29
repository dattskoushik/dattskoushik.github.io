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
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const navLinks = document.querySelector('.nav-links');

        if (mobileMenuBtn && navLinks) {
            mobileMenuBtn.addEventListener('click', () => {
                navLinks.classList.toggle('active');
                const isExpanded = navLinks.classList.contains('active');
                mobileMenuBtn.setAttribute('aria-expanded', isExpanded);
                mobileMenuBtn.innerHTML = isExpanded ? '✕' : '☰';
            });

            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.site-header')) {
                    navLinks.classList.remove('active');
                    mobileMenuBtn.setAttribute('aria-expanded', 'false');
                    mobileMenuBtn.innerHTML = '☰';
                }
            });

            // Close menu on navigation link click
            navLinks.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    navLinks.classList.remove('active');
                    mobileMenuBtn.setAttribute('aria-expanded', 'false');
                    mobileMenuBtn.innerHTML = '☰';
                });
            });
        }
    });
})();

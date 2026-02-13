// Theme Toggle Logic & Mobile Menu
// Uses localStorage to persist preference
// Defaults to 'dark'

(function() {
    function setTheme(theme) {
        document.body.setAttribute('data-theme', theme);
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
    // We need to wait for body to be available if this script is in head?
    // base.html puts it in head.
    // So we should run this on DOMContentLoaded or after body is parsed.
    // However, to prevent flash, it's better to run it immediately if body exists, or wait.

    // Check if body exists (it won't if script is in head)
    if (document.body) {
        setTheme(savedTheme);
    } else {
        // If script is in head, wait for body
        document.addEventListener('DOMContentLoaded', () => {
             // Re-check theme in case it wasn't set (though we want it set asap)
             // But usually, setting it on body in head doesn't work.
             // We should probably move the script to end of body or use documentElement as fallback?
             // Oat requires it on BODY.
             // If I set it on documentElement, Oat won't see it?
             // Oat uses: [data-theme="dark"] { ... }
             // Wait, Oat's CSS usually targets root or body.
             // If Oat's CSS is like: `[data-theme="dark"] { --bg: ... }`, then it works on html too if variables are inherited.
             // But my styles in base.html target `[data-theme="dark"]`.
             // If I put `[data-theme="dark"]` on `html`, `body` inherits variables.
             // Oat documentation says: "data-theme="dark" on body automatically uses the bundled dark theme."
             // If Oat's CSS targets `body[data-theme="dark"]`, then it MUST be on body.
             // If it targets `[data-theme="dark"]`, then html is fine.
             // Let's assume it must be on body.

             // To avoid flash of unstyled content (FOUC) or wrong theme:
             // I should probably move the script to just after <body> open in base.html?
             // Or just use DOMContentLoaded and accept a tiny delay.
             setTheme(savedTheme);
        });
    }

    // Expose toggle function
    window.toggleTheme = function() {
        const current = document.body.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
    };

    // DOM Ready
    document.addEventListener('DOMContentLoaded', () => {
        // Theme Toggle
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.onclick = window.toggleTheme;
            const current = document.body.getAttribute('data-theme') || savedTheme;
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

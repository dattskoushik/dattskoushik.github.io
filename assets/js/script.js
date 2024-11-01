document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Intersection Observer for section animations
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                if (entry.target.hasAttribute('data-animate-children')) {
                    animateChildren(entry.target);
                }
            }
        });
    }, { root: null, rootMargin: '0px', threshold: 0.1 });

    document.querySelectorAll('.section').forEach(section => sectionObserver.observe(section));

    // Active section highlighting
    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, { rootMargin: '-50% 0px -50% 0px' });

    document.querySelectorAll('section[id]').forEach(section => navObserver.observe(section));

    // Initialize theme from localStorage and set up theme toggle
    initializeTheme();
    document.querySelector('.theme-toggle').addEventListener('click', toggleTheme);

    // Mobile menu handling
    document.querySelector('.mobile-menu-toggle').addEventListener('click', toggleMobileMenu);

    // Load blog posts
    loadBlogPosts();
});

// Project filtering with animations
function filterProjects(category) {
    const projects = document.querySelectorAll('.card-project');
    projects.forEach(project => {
        const projectCategory = project.getAttribute('data-category');
        const isVisible = category === 'all' || projectCategory === category;
        
        if (isVisible) {
            project.style.display = 'block';
            setTimeout(() => project.classList.add('visible'), 10);
        } else {
            project.classList.remove('visible');
            setTimeout(() => project.style.display = 'none', 300);
        }
    });
}

// Load blog posts from JSON file with error handling
async function loadBlogPosts() {
    try {
        const response = await fetch('/blog/posts/index.json');
        if (!response.ok) throw new Error('Network response was not ok');
        
        const posts = await response.json();
        const blogContainer = document.querySelector('.posts-grid');
        
        posts.forEach(post => blogContainer.appendChild(createBlogPostElement(post)));
    } catch (error) {
        console.error('Error loading blog posts:', error);
        document.querySelector('.posts-grid').innerHTML = '<p>Error loading posts.</p>';
    }
}

function createBlogPostElement(post) {
    const article = document.createElement('article');
    article.className = 'blog-post animate-fade-in';
    article.innerHTML = `
        <div class="post-meta">
            <span class="post-date">${new Date(post.date).toLocaleDateString()}</span>
            ${post.tags ? `<div class="post-tags">${post.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</div>` : ''}
        </div>
        <h3 class="post-title">${post.title}</h3>
        <p class="post-excerpt">${post.excerpt}</p>
        <a href="${post.url}" class="read-more">Read more →</a>
    `;
    return article;
}

// Toggle mobile menu visibility
function toggleMobileMenu() {
    const nav = document.querySelector('.nav-menu');
    nav.classList.toggle('active');
}

// Theme switching and saving preference
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Initialize theme on page load
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Helper function to animate child elements
function animateChildren(parent) {
    const children = parent.querySelectorAll('.animate-child');
    children.forEach((child, index) => {
        setTimeout(() => {
            child.classList.add('visible');
        }, index * 100);
    });
}

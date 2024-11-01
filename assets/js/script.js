// Navigation handling
document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Intersection Observer for section animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                if (entry.target.hasAttribute('data-animate-children')) {
                    animateChildren(entry.target);
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.section').forEach(section => {
        sectionObserver.observe(section);
    });

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
    }, {
        rootMargin: '-50% 0px -50% 0px'
    });

    document.querySelectorAll('section[id]').forEach(section => {
        navObserver.observe(section);
    });
});

// Project filtering
function filterProjects(category) {
    const projects = document.querySelectorAll('.project-card');
    projects.forEach(project => {
        const projectCategory = project.getAttribute('data-category');
        if (category === 'all' || projectCategory === category) {
            project.style.display = 'block';
            setTimeout(() => project.classList.add('visible'), 10);
        } else {
            project.classList.remove('visible');
            setTimeout(() => project.style.display = 'none', 300);
        }
    });
}

// Blog post loading
async function loadBlogPosts() {
    try {
        const response = await fetch('/blog/posts/index.json');
        const posts = await response.json();
        const blogContainer = document.querySelector('.blog-posts');
        
        posts.forEach(post => {
            const postElement = createBlogPostElement(post);
            blogContainer.appendChild(postElement);
        });
    } catch (error) {
        console.error('Error loading blog posts:', error);
    }
}

function createBlogPostElement(post) {
    const article = document.createElement('article');
    article.className = 'blog-post animate-fade-in';
    article.innerHTML = `
        <div class="post-meta">
            <span class="post-date">${new Date(post.date).toLocaleDateString()}</span>
            ${post.tags ? `<div class="post-tags">${post.tags.map(tag => 
                `<span class="tag">${tag}</span>`).join('')}</div>` : ''}
        </div>
        <h3 class="post-title">${post.title}</h3>
        <p class="post-excerpt">${post.excerpt}</p>
        <a href="${post.url}" class="read-more">Read more →</a>
    `;
    return article;
}

// Mobile menu handling
function toggleMobileMenu() {
    const nav = document.querySelector('.nav-menu');
    nav.classList.toggle('active');
}

// Theme switching
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Initialize theme from localStorage
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Helper function to animate children elements
function animateChildren(parent) {
    const children = parent.querySelectorAll('.animate-child');
    children.forEach((child, index) => {
        setTimeout(() => {
            child.classList.add('visible');
        }, index * 100);
    });
}
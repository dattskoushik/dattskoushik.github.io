import markdown
import os
import json
from pathlib import Path
from datetime import datetime

# Configuration
ARTICLES_DIR = "blog/articles"
ARTICLES_JSON = "blog/articles.json"
OUTPUT_DIR = "blog"
SEARCH_INDEX_FILE = "blog/search.json"
TEMPLATES_DIR = "templates"

# Ensure templates directory exists
Path(TEMPLATES_DIR).mkdir(exist_ok=True)

# Article Template
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} | Suchindra Koushik</title>
    <meta name="description" content="{{DESCRIPTION}}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/main.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <script src="../assets/js/theme.js"></script>
</head>
<body>

    <header class="site-header">
        <div class="container">
            <a href="../" class="logo">Suchindra Koushik</a>
            <button class="mobile-menu-btn" aria-label="Menu" aria-expanded="false">☰</button>
            <nav class="nav-links">
                <a href="../">Home</a>
                <a href="index.html" class="active">Writing</a>
                <a href="../projects.html">Projects</a>
                <a href="../about.html">About</a>
                <a href="../resume.html">Resume</a>
                <button id="theme-toggle" aria-label="Toggle theme">☀️</button>
            </nav>
        </div>
    </header>

    <main class="container">
        <article class="hero" style="padding-bottom: var(--space-md); max-width: 800px; margin: 0 auto;">
            <a href="index.html" style="font-size: 0.875rem; color: var(--text-muted); text-decoration: none; display: inline-block; margin-bottom: var(--space-sm);">&larr; Back to Writing</a>
            <div class="hero-meta" style="margin-top: 0; margin-bottom: var(--space-sm);">
                {{CATEGORY}} • {{DATE}} • {{READ_TIME}}
            </div>
            <h1 style="margin-bottom: var(--space-md);">{{TITLE}}</h1>
        </article>

        <div class="post-content">
            {{CONTENT}}
        </div>
    </main>

    <footer class="site-footer container">
        <div class="social-links">
            <a href="https://github.com/dattskoushik" target="_blank">GitHub</a>
            <a href="https://linkedin.com/in/suchindrakoushik" target="_blank">LinkedIn</a>
            <a href="https://instagram.com/dattskoushik" target="_blank">Instagram</a>
        </div>
        <p class="copyright">&copy; <script>document.write(new Date().getFullYear())</script> Suchindra Koushik. All rights reserved.</p>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-go.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-rust.min.js"></script>
</body>
</html>
"""

# Blog Index Template
INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Writing | Suchindra Koushik</title>
    <meta name="description" content="Technical articles and thoughts on backend engineering, data systems, and software architecture.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/main.css">
    <script src="../assets/js/theme.js"></script>
</head>
<body>

    <header class="site-header">
        <div class="container">
            <a href="../" class="logo">Suchindra Koushik</a>
            <button class="mobile-menu-btn" aria-label="Menu" aria-expanded="false">☰</button>
            <nav class="nav-links">
                <a href="../">Home</a>
                <a href="index.html" class="active">Writing</a>
                <a href="../projects.html">Projects</a>
                <a href="../about.html">About</a>
                <a href="../resume.html">Resume</a>
                <button id="theme-toggle" aria-label="Toggle theme">☀️</button>
            </nav>
        </div>
    </header>

    <main class="container" style="padding-top: var(--space-xl);">
        <h1>Writing</h1>
        <p class="hero-subtitle" style="margin-bottom: var(--space-xl);">
            Thoughts on backend architecture, data reliability, and engineering practices.
        </p>

        <!-- Search Bar -->
        <div style="margin-bottom: var(--space-lg); max-width: 800px;">
            <input type="text" id="search-input" placeholder="Search articles..."
                style="width: 100%; padding: var(--space-sm); border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-primary); font-family: var(--font-sans); font-size: 1rem;">
        </div>

        <div id="articles-list" class="card-grid" style="grid-template-columns: 1fr; max-width: 800px;">
            {{ARTICLES_LIST}}
        </div>
    </main>

    <footer class="site-footer container">
        <div class="social-links">
            <a href="https://github.com/dattskoushik" target="_blank">GitHub</a>
            <a href="https://linkedin.com/in/suchindrakoushik" target="_blank">LinkedIn</a>
            <a href="https://instagram.com/dattskoushik" target="_blank">Instagram</a>
        </div>
        <p class="copyright">&copy; <script>document.write(new Date().getFullYear())</script> Suchindra Koushik. All rights reserved.</p>
    </footer>

    <script>
        // Simple client-side search
        let articles = [];

        fetch('search.json')
            .then(response => response.json())
            .then(data => {
                articles = data;
                articles.forEach(a => {
                    a.searchStr = (a.title + " " + a.tags.join(" ") + " " + a.summary).toLowerCase();
                });
            })
            .catch(err => console.error("Could not load search index", err));

        const searchInput = document.getElementById('search-input');
        const list = document.getElementById('articles-list');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                const filtered = term ? articles.filter(a => a.searchStr.includes(term)) : articles;
                render(filtered);
            });
        }

        function render(items) {
            if (items.length === 0) {
                list.innerHTML = '<p style="color: var(--text-secondary);">No articles found.</p>';
                return;
            }
            list.innerHTML = items.map(item => `
                <article class="card" style="flex-direction: row; align-items: center; border: none; background: transparent; padding: var(--space-md) 0; border-bottom: 1px solid var(--border-color); border-radius: 0;">
                    <div style="flex: 1;">
                        <div class="card-meta">${item.category} • <time>${item.date}</time> • ${item.readTime}</div>
                        <h3><a href="${item.url}">${item.title}</a></h3>
                        <p class="card-excerpt">${item.summary}</p>
                    </div>
                </article>
            `).join('');
        }
    </script>
</body>
</html>
"""


def parse_markdown_metadata(content):
    """
    Parse metadata from markdown files.
    Supports frontmatter or inline metadata.
    """
    lines = content.split('\n')
    title = "Untitled"
    date = "Unknown Date"
    category = "Uncategorized"
    body_start_idx = 0

    # Try to extract title from first H1
    if len(lines) > 0 and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body_start_idx = 1

    # Look for metadata section
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start_idx = i + 1
            break

        if line.startswith("**Date:**"):
            date = line.replace("**Date:**", "").strip()
        elif line.startswith("**Category:**"):
            category = line.replace("**Category:**", "").strip()

    body = "\n".join(lines[body_start_idx:]).strip()

    # Extract summary
    summary = ""
    for line in body.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            summary = stripped
            if len(summary) > 160:
                summary = summary[:157] + "..."
            break

    return {
        "title": title,
        "date": date,
        "category": category,
        "body": body,
        "summary": summary
    }


def load_articles_metadata():
    """Load articles.json if it exists, otherwise return empty dict."""
    if os.path.exists(ARTICLES_JSON):
        with open(ARTICLES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"articles": []}


def generate_article_html(article_meta, markdown_content):
    """Generate HTML for a single article."""
    html_body = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables', 'nl2br'])
    
    html = ARTICLE_TEMPLATE.replace("{{TITLE}}", article_meta['title'])
    html = html.replace("{{DATE}}", article_meta['date'])
    html = html.replace("{{CATEGORY}}", article_meta['category'])
    html = html.replace("{{READ_TIME}}", article_meta.get('readTime', '5 min'))
    html = html.replace("{{CONTENT}}", html_body)
    html = html.replace("{{DESCRIPTION}}", article_meta['excerpt'])
    
    return html


def generate_blog_index(articles_data):
    """Generate blog/index.html from articles data."""
    articles_html = ""
    
    for article in articles_data:
        articles_html += f'''
        <article class="card" style="flex-direction: row; align-items: center; border: none; background: transparent; padding: var(--space-md) 0; border-bottom: 1px solid var(--border-color); border-radius: 0;">
            <div style="flex: 1;">
                <div class="card-meta">{article['category']} • <time>{article['date']}</time> • {article.get('readTime', '5 min')}</div>
                <h3><a href="{article['slug']}.html">{article['title']}</a></h3>
                <p class="card-excerpt">{article['excerpt']}</p>
            </div>
        </article>
        '''
    
    html = INDEX_TEMPLATE.replace("{{ARTICLES_LIST}}", articles_html)
    
    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated {output_path}")


def generate_search_index(articles_data):
    """Generate search.json for client-side search."""
    search_data = []
    
    for article in articles_data:
        search_data.append({
            "title": article['title'],
            "date": article['date'],
            "category": article['category'],
            "summary": article['excerpt'],
            "tags": article.get('tags', []),
            "readTime": article.get('readTime', '5 min'),
            "url": f"{article['slug']}.html"
        })
    
    with open(SEARCH_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2)
    
    print(f"✓ Generated {SEARCH_INDEX_FILE}")


def build_blog():
    """Main build function."""
    print("=" * 60)
    print("Building static blog...")
    print("=" * 60)
    
    # Ensure output directory exists
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Load articles metadata
    metadata = load_articles_metadata()
    articles = metadata.get('articles', [])
    
    if not articles:
        print("⚠ No articles found in articles.json")
        print("  Create blog/articles.json with article metadata")
        return
    
    # Sort articles by date (newest first)
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # Generate individual article pages
    print(f"\nGenerating {len(articles)} article pages...")
    for article in articles:
        slug = article['slug']
        md_file = os.path.join(ARTICLES_DIR, f"{slug}.md")
        
        if not os.path.exists(md_file):
            print(f"⚠ Markdown file not found: {md_file}")
            continue
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Parse metadata from markdown (fallback if needed)
        parsed = parse_markdown_metadata(md_content)
        
        # Merge metadata (JSON takes precedence)
        article_data = {
            'title': article.get('title', parsed['title']),
            'date': article.get('date', parsed['date']),
            'category': article.get('category', parsed['category']),
            'excerpt': article.get('excerpt', parsed['summary']),
            'readTime': article.get('readTime', '5 min')
        }
        
        # Generate HTML
        html = generate_article_html(article_data, parsed['body'])
        
        # Write to file
        output_file = os.path.join(OUTPUT_DIR, f"{slug}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✓ {slug}.html")
    
    # Generate blog index
    print("\nGenerating blog index...")
    generate_blog_index(articles)
    
    # Generate search index
    print("Generating search index...")
    generate_search_index(articles)
    
    print("\n" + "=" * 60)
    print("✓ Build complete!")
    print("=" * 60)


if __name__ == "__main__":
    build_blog()

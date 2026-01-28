import markdown
import os
import json

# Configuration
ARTICLES_DIR = "blog/articles"
OUTPUT_DIR = "blog"
SEARCH_INDEX_FILE = "blog/search.json"

# Template for Article Pages
# Using placeholders like {{TITLE}} to avoid collision with CSS/JS braces
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
                {{CATEGORY}} • {{DATE}}
            </div>
            <h1 style="margin-bottom: var(--space-md);">{{TITLE}}</h1>
        </article>

        <div class="post-content">
            {{CONTENT}}
        </div>
    </main>

    <footer class="site-footer container">
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

# Template for Blog Index
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
        <p class="copyright">&copy; <script>document.write(new Date().getFullYear())</script> Suchindra Koushik. All rights reserved.</p>
    </footer>

    <script>
        // Simple client-side search
        let articles = [];

        fetch('search.json')
            .then(response => response.json())
            .then(data => {
                articles = data;
                // Normalize data for client-side use
                articles.forEach(a => {
                    a.searchStr = (a.title + " " + a.tags + " " + a.summary).toLowerCase();
                });
            })
            .catch(err => console.error("Could not load search index", err));

        const searchInput = document.getElementById('search-input');
        const list = document.getElementById('articles-list');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                const filtered = articles.filter(a => a.searchStr.includes(term));
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
                        <div class="card-meta">${item.tags} • <time>${item.date}</time></div>
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

def parse_metadata(content):
    lines = content.split('\n')
    title = "Untitled"
    date = "Unknown Date"
    category = "Uncategorized"
    body_start_idx = 0

    if len(lines) > 0 and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body_start_idx = 1

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start_idx = i + 1
            break

        if line.startswith("**Date:**"):
            date = line.replace("**Date:**", "").strip()
        elif line.startswith("**Category:**"):
            category = line.replace("**Category:**", "").strip()

    body = "\n".join(lines[body_start_idx:]).strip()

    summary = ""
    for line in body.split('\n'):
        if line.strip():
            summary = line.strip()
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

def build_blog():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    search_index = []
    articles_data = []

    if os.path.exists(ARTICLES_DIR):
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".md")]
    else:
        files = []
        print(f"Warning: {ARTICLES_DIR} does not exist.")

    for filename in files:
        filepath = os.path.join(ARTICLES_DIR, filename)
        with open(filepath, "r") as f:
            content = f.read()

        meta = parse_metadata(content)

        html_body = markdown.markdown(meta['body'], extensions=['fenced_code', 'tables'])

        output_filename = filename.replace(".md", ".html")
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        final_html = ARTICLE_TEMPLATE.replace("{{TITLE}}", meta['title'])
        final_html = final_html.replace("{{DATE}}", meta['date'])
        final_html = final_html.replace("{{CATEGORY}}", meta['category'])
        final_html = final_html.replace("{{CONTENT}}", html_body)
        final_html = final_html.replace("{{DESCRIPTION}}", meta['summary'])

        with open(output_path, "w") as f:
            f.write(final_html)

        print(f"Generated {output_path}")

        article_info = {
            "title": meta['title'],
            "date": meta['date'],
            "tags": meta['category'],
            "summary": meta['summary'],
            "url": output_filename
        }
        search_index.append(article_info)
        articles_data.append(article_info)

    with open(SEARCH_INDEX_FILE, "w") as f:
        json.dump(search_index, f)
    print(f"Generated {SEARCH_INDEX_FILE}")

    articles_html = ""
    for item in articles_data:
        articles_html += f'''
        <article class="card" style="flex-direction: row; align-items: center; border: none; background: transparent; padding: var(--space-md) 0; border-bottom: 1px solid var(--border-color); border-radius: 0;">
            <div style="flex: 1;">
                <div class="card-meta">{item['tags']} • <time>{item['date']}</time></div>
                <h3><a href="{item['url']}">{item['title']}</a></h3>
                <p class="card-excerpt">{item['summary']}</p>
            </div>
        </article>
        '''

    final_index_html = INDEX_TEMPLATE.replace("{{ARTICLES_LIST}}", articles_html)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(final_index_html)
    print("Generated blog/index.html")

if __name__ == "__main__":
    build_blog()

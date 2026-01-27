import markdown
import os

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Suchindra Koushik</title>
    <meta name="description" content="Technical article by Suchindra Koushik.">
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
            <nav class="nav-links">
                <a href="../">Home</a>
                <a href="index.html" class="active">Writing</a>
                <a href="../about.html">About</a>
                <button id="theme-toggle" aria-label="Toggle theme">☀️</button>
            </nav>
        </div>
    </header>

    <main class="container">
        <article class="hero" style="padding-bottom: var(--space-md); max-width: 800px; margin: 0 auto;">
            <a href="index.html" style="font-size: 0.875rem; color: var(--text-muted); text-decoration: none; display: inline-block; margin-bottom: var(--space-sm);">&larr; Back to Writing</a>
            <div class="hero-meta" style="margin-top: 0; margin-bottom: var(--space-sm);">
                Technical Article
            </div>
        </article>

        <div class="post-content">
            {content}
        </div>
    </main>

    <footer class="site-footer container">
        <p class="copyright">&copy; <script>document.write(new Date().getFullYear())</script> Suchindra Koushik. All rights reserved.</p>
    </footer>
</body>
</html>
"""

def build_blog():
    articles_dir = "blog/articles"
    output_dir = "blog"

    mapping = {
        "postgres-query-planning.md": "postgres-query-planning.html",
        "batch-data-pipelines.md": "batch-data-pipelines.html",
        "python-performance.md": "python-performance.html"
    }

    for filename, output_name in mapping.items():
        filepath = os.path.join(articles_dir, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filepath}, not found")
            continue

        with open(filepath, "r") as f:
            md_content = f.read()

        # Basic extraction of title (first h1)
        title = "Article"
        lines = md_content.split('\n')
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

        final_html = TEMPLATE.format(title=title, content=html_content)

        out_path = os.path.join(output_dir, output_name)
        with open(out_path, "w") as f:
            f.write(final_html)
        print(f"Generated {out_path}")

if __name__ == "__main__":
    build_blog()

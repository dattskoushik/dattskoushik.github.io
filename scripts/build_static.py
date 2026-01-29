import markdown
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Configuration
ARTICLES_DIR = "blog/articles"
ARTICLES_JSON = "blog/articles.json"
PHOTOS_JSON = "assets/images/gallery/photos.json"
POEMS_JSON = "assets/poetry/poems.json"
BLOG_OUTPUT_DIR = "blog"
SEARCH_INDEX_FILE = "blog/search.json"
TEMPLATES_DIR = "templates"

def load_json_or_fail(filepath):
    """Load JSON file or exit with error if missing/invalid."""
    if not os.path.exists(filepath):
        print(f"ERROR: Required file not found: {filepath}")
        sys.exit(1)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        sys.exit(1)

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

    # Extract summary if not provided
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

def build_site():
    print("=" * 60)
    print("Building static site with Jinja2...")
    print("=" * 60)

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    # Ensure output directories exist
    Path(BLOG_OUTPUT_DIR).mkdir(exist_ok=True)

    # Load Data
    print("Loading content data...")
    articles_data = load_json_or_fail(ARTICLES_JSON).get('articles', [])
    photos_data = load_json_or_fail(PHOTOS_JSON).get('photos', [])
    poems_data = load_json_or_fail(POEMS_JSON).get('poems', [])

    if not articles_data:
        print("WARNING: No articles found in articles.json")

    # --- Generate Blog Articles ---
    print(f"\nProcessing {len(articles_data)} articles...")
    
    # Sort articles by date (newest first)
    articles_data.sort(key=lambda x: x['date'], reverse=True)

    processed_articles = []

    for article in articles_data:
        slug = article['slug']
        md_file = os.path.join(ARTICLES_DIR, f"{slug}.md")
        
        if not os.path.exists(md_file):
            print(f"ERROR: Markdown file missing for article '{slug}': {md_file}")
            sys.exit(1)
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        parsed = parse_markdown_metadata(md_content)
        
        # Merge metadata
        final_article = {
            'slug': slug,
            'title': article.get('title', parsed['title']),
            'date': article.get('date', parsed['date']),
            'category': article.get('category', parsed['category']),
            'excerpt': article.get('excerpt', parsed['summary']),
            'readTime': article.get('readTime', '5 min'),
            'tags': article.get('tags', []),
            'url': f"{slug}.html" # Relative to blog/
        }

        # Render Content
        html_body = markdown.markdown(parsed['body'], extensions=['fenced_code', 'tables', 'nl2br'])

        # Render Template
        template = env.get_template('article.html')
        html_output = template.render(
            root="..",
            active_page="blog",
            title=final_article['title'],
            description=final_article['excerpt'],
            category=final_article['category'],
            date=final_article['date'],
            read_time=final_article['readTime'],
            content=html_body
        )

        output_path = os.path.join(BLOG_OUTPUT_DIR, f"{slug}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"  ✓ {slug}.html")
        processed_articles.append(final_article)

    # --- Generate Blog Index ---
    print("\nGenerating blog index...")
    template = env.get_template('blog_index.html')
    html_output = template.render(
        root="..",
        active_page="blog",
        title="Writing",
        description="Technical articles and thoughts on backend engineering.",
        articles=processed_articles
    )
    with open(os.path.join(BLOG_OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html_output)
    print(f"  ✓ blog/index.html")

    # --- Generate Search Index ---
    print("\nGenerating search index...")
    search_data = []
    for article in processed_articles:
        search_data.append({
            "title": article['title'],
            "date": article['date'],
            "category": article['category'],
            "summary": article['excerpt'],
            "tags": article['tags'],
            "readTime": article['readTime'],
            "url": article['url']
        })
    
    with open(SEARCH_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2)
    print(f"  ✓ {SEARCH_INDEX_FILE}")

    # --- Generate About Page ---
    print("\nGenerating about page...")
    template = env.get_template('about.html')
    html_output = template.render(
        root=".",
        active_page="about",
        title="About",
        description="About M S Suchindra Datta Koushik, Software engineer - Backend and Data.",
        photos=photos_data,
        poems=poems_data
    )
    with open("about.html", 'w', encoding='utf-8') as f:
        f.write(html_output)
    print(f"  ✓ about.html")

    print("\n" + "=" * 60)
    print("✓ Build complete!")
    print("=" * 60)

if __name__ == "__main__":
    build_site()

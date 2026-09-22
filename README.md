# Personal Website

A static personal website built with plain HTML, CSS, and JavaScript, hosted on GitHub Pages.

## 🏗️ Architecture

This site uses a **data-driven static site** approach:

- **Content as Data**: Articles, photos, and poems are defined in JSON files
- **Build-Time Generation**: Python script generates HTML from markdown + JSON
- **Zero Runtime Dependencies**: Pure HTML/CSS/JS for maximum performance
- **GitHub Actions**: Automated deployment on every push

## 📁 Structure

```
├── blog/
│   ├── articles.json          # Article metadata (single source of truth)
│   ├── articles/*.md          # Markdown source files
│   ├── *.html                 # Generated article pages
│   ├── index.html             # Generated blog index
│   └── search.json            # Generated search index
├── assets/
│   ├── images/gallery/
│   ├── poetry/
├── data/
│   ├── photos.json        # Photography metadata
│   └── poems.json         # Poetry collection
│   └── js/theme.js            # Theme switcher
├── css/
│   ├── main.css               # Main styles
│   └── variables.css          # CSS custom properties
├── scripts/
│   └── build_static.py        # Static site generator
└── .github/workflows/
    └── deploy.yml             # CI/CD pipeline
```

## ✍️ Content Workflow

### Adding a New Article

1. **Create markdown file:**
   ```bash
   touch blog/articles/my-new-post.md
   ```

2. **Write content:**
   ```markdown
   # My New Post

   **Date:** 2024-03-20
   **Category:** Backend Engineering

   ---

   Your article content here...
   ```

3. **Add metadata to `blog/articles.json`:**
   ```json
   {
     "slug": "my-new-post",
     "title": "My New Post",
     "date": "2024-03-20",
     "category": "Backend Engineering",
     "excerpt": "Brief description...",
     "tags": ["backend", "python"],
     "readTime": "5 min"
   }
   ```

4. **Build and preview locally:**
   ```bash
   python scripts/build_static.py
   open blog/my-new-post.html
   ```

5. **Deploy:**
   ```bash
   git add blog/articles.json blog/articles/my-new-post.md
   git commit -m "Add: My New Post"
   git push
   ```
   GitHub Actions will automatically build and deploy.

### Adding Photography

1. **Add images to `assets/images/gallery/`**

2. **Update `data/photos.json`:**
   ```json
   {
     "id": "sunset-2024",
     "path": "/assets/images/gallery/sunset-2024.jpg",
     "thumbnail": "/assets/images/gallery/sunset-2024-thumb.jpg",
     "caption": "Golden hour",
     "date": "2024-03-20",
     "tags": ["landscape"]
   }
   ```

3. **The about page will automatically load and display new photos**

### Adding Poetry

Update `data/poems.json`:
```json
{
  "title": "New Poem",
  "date": "2024-03-20",
  "lines": [
    "First line",
    "Second line"
  ]
}
```

## 🛠️ Local Development

```bash
# Generate static files
python scripts/build_static.py

# Serve locally (Python 3)
python -m http.server 8000

# Open in browser
open http://localhost:8000
```

## 🚀 Deployment

Deployment is automatic via GitHub Actions when you push to `main`:

1. Push changes to GitHub
2. GitHub Actions runs `build_static.py`
3. Site is deployed to GitHub Pages

Manual deployment:
```bash
git push origin main
```

## 📝 Maintenance Philosophy

**What to Keep Simple:**
- Static pages (about, resume, projects) → Direct HTML
- Styling → CSS custom properties (no preprocessor needed)
- Theme switching → Vanilla JS

**What's Data-Driven:**
- Blog articles → `articles.json` + markdown
- Photography → `photos.json`
- Poetry → `poems.json`

**When to Refactor:**
- [ ] When `build_static.py` exceeds 300 lines → Consider 11ty/Hugo
- [ ] When you have >50 articles → Evaluate static site generator
- [ ] When navigation changes require editing 10+ files → Add templating

## 🔧 Dependencies

**Runtime:** None (pure HTML/CSS/JS)

**Build-time:**
- Python 3.11+
- `markdown` library

**Development:**
- Any text editor
- Git
- Web browser

## 📊 Performance

- ✅ Zero JavaScript frameworks (< 10KB total JS)
- ✅ No build-time CSS processing needed
- ✅ Client-side search with <5KB JSON
- ✅ Static HTML = instant page loads
- ✅ Lazy-loaded images in gallery

## 🎯 Design Principles

1. **Simplicity Over Cleverness**
2. **Content in JSON, Presentation in Templates**
3. **No Premature Optimization**
4. **Manual is Fine Until It Hurts**
5. **GitHub Actions for Automation**

---

**License:** MIT  
**Author:** Suchindra Koushik
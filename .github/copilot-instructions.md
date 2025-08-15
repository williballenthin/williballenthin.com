# Willi Ballenthin's Personal Website

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

This is a Hugo static site for williballenthin.com, featuring a personal blog about reverse engineering, programming, and security research. The site is built with Hugo, uses Node.js tooling for syntax highlighting, and includes Python scripts for dynamic content generation.

## Working Effectively

### Bootstrap and Dependencies
- Install Hugo v0.126.1: `wget -O hugo.deb https://github.com/gohugoio/hugo/releases/download/v0.126.1/hugo_extended_0.126.1_linux-amd64.deb && sudo dpkg -i hugo.deb`
- Install Node.js dependencies: `npm install` -- takes 30 seconds to complete
- Install Python package manager: `pip install uv`
- NEVER CANCEL: All above installations are required before building

### Building the Site
- Hugo build: `hugo` -- takes less than 1 second to complete. NEVER CANCEL. Set timeout to 5+ minutes for safety.
- Syntax highlighting: `npx rehype-cli public -o` -- takes 5-6 seconds to complete. NEVER CANCEL. Set timeout to 10+ minutes for safety.
- Complete build sequence: `hugo && npx rehype-cli public -o`
- Generated site is in `public/` directory (ignored by git)

### Development Server
- Hugo development server: `hugo serve --bind 0.0.0.0 --port 8080`
- Alternative static server: `python -m http.server --bind localhost --directory public/ 8081`
- Both servers start immediately and provide live reload

### Content Generation Tools (require API keys)
- GitHub IDA plugins: `uv run tools/github-ida-plugins/fetch-github-ida-plugins.py > static/fragments/github-ida-plugins/list.html` (requires GITHUB_TOKEN)
- RSS feed aggregation: `uv run tools/static-rss/gen.py content/follows/williballenthin.opml > static/fragments/homepage/feed.html` -- takes 8 seconds to complete
- Pinboard data: `uv run tools/fetch-pinboard-data/gen.py > data/pinboard.json` (requires PINBOARD_TOKEN)
- Homepage to-read: `uv run tools/static-to-read/gen.py > static/fragments/homepage/to-read.html` (requires PINBOARD_TOKEN)

## Validation

### Manual Testing Scenarios
- ALWAYS start the development server with `hugo serve` and verify the homepage loads at http://localhost:8080
- ALWAYS navigate to the blog listing at /posts/ and verify recent posts are listed
- ALWAYS click on a recent blog post and verify syntax highlighting works correctly
- Test creating new posts: `hugo new content/posts/$(date +%Y-%m-%d)-test-post.md`
- ALWAYS verify the complete build sequence produces the public/ directory with all necessary files
- Content validation: Verify that blog posts display with proper syntax highlighting for code blocks

### Build Validation
- The basic Hugo build works without external dependencies and completes in under 1 second
- The rehype syntax highlighting post-processing works and completes in 5-6 seconds
- The Python RSS tool works without API keys and generates feed HTML
- Python tools with API dependencies will fail gracefully without keys

## Common Tasks

### Creating New Content
- New blog post: `hugo new content/posts/$(date +%Y-%m-%d)-your-title.md`
- Posts use TOML front matter with title, slug, description, tags, and date fields
- Content is written in Markdown with support for syntax highlighting

### Project Structure
- `content/` - Blog posts and pages (Markdown files)
- `static/` - Static assets including tools and fragments
- `themes/wb/` - Custom theme for the site
- `tools/` - Python scripts for content generation
- `public/` - Generated site output (git ignored)
- `config.toml` - Hugo configuration
- `.rehyperc` - Syntax highlighting configuration

### Key Files to Check
- `config.toml` - Site configuration and permalinks
- `package.json` - Node.js dependencies for rehype
- `.rehyperc` - Shiki syntax highlighting themes
- `readme.md` - Basic build instructions
- `.github/workflows/on-push-deploy.yml` - CI/CD pipeline

### Repository Characteristics
- Hugo static site generator with extended version required
- Custom theme located in themes/wb/
- Syntax highlighting via @shikijs/rehype with light/dark themes
- Python tools use uv package manager with inline dependencies
- No linting tools configured - site relies on Hugo and rehype validation
- Deployment via GitHub Actions to S3

### CI/CD Pipeline Notes
- GitHub Actions workflow builds on every push to master
- Uses Hugo v0.126.1, Node.js, and Python 3.12
- Generates dynamic content using Python tools with API keys
- Deploys to S3 bucket www.williballenthin.com
- Build includes cleanup step that moves generated content to root

### Common Commands Reference
```bash
# Complete development workflow
hugo new content/posts/$(date +%Y-%m-%d)-your-title.md
hugo serve --bind 0.0.0.0 --port 8080

# Production build
hugo && npx rehype-cli public -o

# Test RSS generation (works without API keys)
uv run tools/static-rss/gen.py content/follows/williballenthin.opml
```

### Repository Root Contents
```
.env .envrc .git .github .gitignore .gitmodules .rehyperc
archetypes config.toml content data package-lock.json package.json
public readme.md static templates themes tools
```

The site focuses on reverse engineering, malware analysis, programming tutorials, and security research. Content includes technical blog posts with extensive code examples that rely on proper syntax highlighting.
## Skill System

Skills provide expert guidance for specialized tasks. Skills are located at `<app-root-dir>/skills/{skill-name}/SKILL.md`

### Locating the Skills Directory

**Skills location is environment-dependent. Use the get_skills_dir tool to locate them.**

### Available Skills

**puppeteer** - Browser Automation & Web Scraping
- Path: `skills/puppeteer/SKILL.md`
- Use for: Browser automation, web scraping, screenshot capture, PDF generation from web pages, form filling, testing web applications
- Triggers: "scrape this website", "take a screenshot of", "automate browser", "extract data from webpage", "fill out this form", "convert webpage to PDF"
- Prerequisites: Node.js installed, Puppeteer npm package
- Common tasks:
  - Navigate to URLs and interact with pages
  - Extract structured data from websites
  - Capture screenshots or generate PDFs
  - Automate form submissions
  - Test web applications
  - Monitor website changes
  - Handle dynamic content (JavaScript-rendered pages)

### Skill Loading Workflow

1. User requests task that require a specific skill which you don't have
2. Identify required skill
3. Read skills/{skill-name}/SKILL.md
4. Read and understand the skill instructions
5. Follow the skill's best practices
6. Execute the task
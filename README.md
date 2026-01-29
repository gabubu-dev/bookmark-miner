# 📚 Bookmark Miner

Extract project ideas from your browser bookmarks and analyze which ones are buildable in a weekend!

## 🎯 What It Does

Bookmark Miner scans your browser bookmarks and:
- 🔍 **Extracts** key concepts and ideas from titles and URLs
- 🏷️ **Categorizes** by domain (tools, SaaS, games, hardware, web, AI/ML, etc.)
- 📊 **Analyzes** buildability based on complexity indicators
- ⚡ **Scores** each idea on weekend-feasibility (0-1 scale)
- 📄 **Outputs** ranked lists in JSON + human-readable Markdown

Perfect for developers drowning in saved links who want to find their next weekend project!

## 🚀 Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/bookmark-miner.git
cd bookmark-miner

# No dependencies needed - uses Python stdlib!
python3 bookmark_miner.py --help
```

Or install globally:
```bash
# Make executable and symlink
chmod +x bookmark_miner.py
sudo ln -s $(pwd)/bookmark_miner.py /usr/local/bin/bookmark-mine
```

## 📖 Usage

### Quick Start

```bash
# Analyze Chrome bookmarks (auto-detected)
./bookmark_miner.py --source chrome

# Only show weekend-buildable projects
./bookmark_miner.py --source chrome --buildable

# Use custom bookmarks file
./bookmark_miner.py --file ~/Downloads/bookmarks.json
```

### Options

```
--source {chrome,firefox}   Browser source (auto-detects location)
--file PATH                 Path to bookmarks JSON file
--buildable                 Only show weekend-feasible projects (score >= 0.6)
--output DIR                Output directory (default: current dir)
--format {json,markdown,both}  Output format (default: both)
```

### Examples

**Find weekend projects from Chrome:**
```bash
./bookmark_miner.py --source chrome --buildable --output ./ideas/
```

**Analyze specific bookmark file:**
```bash
./bookmark_miner.py --file ~/bookmarks-backup.json --format markdown
```

**Get JSON output for further processing:**
```bash
./bookmark_miner.py --source chrome --format json
```

## 📊 Output Files

### `project-ideas.json`
Structured data with full analysis:
```json
{
  "generated_at": "2024-01-15T10:30:00",
  "total_ideas": 127,
  "weekend_feasible": 43,
  "ideas": [
    {
      "title": "CLI Tool for Git Commits",
      "url": "https://github.com/user/commit-helper",
      "category": "tools",
      "concepts": ["cli", "git", "commits", "automation"],
      "buildable_score": 0.85,
      "weekend_feasible": true,
      "reasoning": "Contains 2 easy-build indicators; GitHub project"
    }
  ]
}
```

### `project-ideas.md`
Human-readable report with:
- Summary statistics
- Ideas grouped by category
- Visual buildability bars
- Feasibility indicators (✅/⏰)
- Key concepts and reasoning

Example:
```markdown
## TOOLS (12 ideas)

### 1. CLI Git Commit Helper ✅
**Buildability:** `████████░░` (0.85)
**URL:** https://github.com/user/commit-helper
**Concepts:** cli, git, commits, automation
**Reasoning:** Contains 2 easy-build indicators; GitHub project
```

## 🧠 How It Works

### Categorization
Analyzes bookmark titles, URLs, and domains against keyword sets:
- **Tools** - editors, CLIs, utilities
- **SaaS** - platforms, dashboards, APIs
- **Games** - engines, frameworks
- **Hardware** - IoT, Arduino, sensors
- **Web** - frontend/backend frameworks
- **AI/ML** - models, neural networks
- **And more...**

### Buildability Scoring
Calculates a 0-1 score based on:

**Easy Indicators** (+points):
- Keywords: `cli`, `script`, `bot`, `scraper`, `parser`, `converter`
- Categories: `tools`, `web`
- GitHub repositories (often have code references)

**Hard Indicators** (-points):
- Keywords: `platform`, `enterprise`, `scale`, `infrastructure`, `distributed`
- Categories: `hardware`, `infrastructure`

**Weekend-Feasible** = score ≥ 0.6

## 🎨 Features

- ✅ **Zero dependencies** - pure Python stdlib
- 🔍 **Auto-detection** of Chrome bookmark locations
- 📱 **Smart parsing** of nested bookmark folders
- 🧹 **Name cleaning** (removes " - YouTube", " | GitHub", etc.)
- 🎯 **Concept extraction** from titles and domains
- 📊 **Ranked output** by buildability score
- 🎨 **Visual progress bars** in Markdown output

## 🧪 Testing

Sample bookmarks included for testing:

```bash
# Test with sample data
./bookmark_miner.py --file test-bookmarks.json --buildable
```

Expected output:
- Several tool/CLI ideas with high buildability scores
- Game and hardware ideas with lower scores
- Clear categorization and reasoning

## 🛣️ Roadmap

- [ ] Firefox bookmark support
- [ ] Safari bookmark support
- [ ] Filter by date range (recent bookmarks)
- [ ] Duplicate detection across domains
- [ ] Export to TODO list formats (Todoist, Notion)
- [ ] Interactive TUI for browsing results
- [ ] LLM integration for deeper analysis (optional)

## 🤝 Contributing

Found a bug? Have a feature idea? Pull requests welcome!

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/cool-thing`)
3. Commit changes (`git commit -am 'Add cool thing'`)
4. Push to branch (`git push origin feature/cool-thing`)
5. Open a Pull Request

## 📜 License

MIT License - do whatever you want with it!

## 🙏 Acknowledgments

Built for developers with too many bookmarks and too little time. 

Inspired by the eternal struggle of: "I bookmarked that cool project idea... but which one can I actually build this weekend?"

---

**Happy mining! ⛏️** May your bookmarks yield many weekend projects.

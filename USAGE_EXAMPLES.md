# Usage Examples

## Quick Test

```bash
# Test with sample data
./bookmark_miner.py --file test-bookmarks.json --buildable
```

**Output:**
```
📚 Parsing bookmarks from: test-bookmarks.json
✓ Found 11 bookmarks
🔍 Analyzing for project ideas...
✓ Generated 6 project ideas
✅ 6 are weekend-feasible
✓ Saved JSON to ./project-ideas.json
✓ Saved Markdown to ./project-ideas.md

🎉 Done! Happy building!
```

## Real Chrome Bookmarks

```bash
# Auto-detect Chrome bookmarks and filter to weekend projects
./bookmark_miner.py --source chrome --buildable --output ./weekend-ideas/
```

This will:
- Find your Chrome bookmarks automatically
- Analyze all bookmarks for project ideas
- Filter to only weekend-feasible projects (score ≥ 0.6)
- Save results to `./weekend-ideas/`

## Custom Analysis

```bash
# Analyze exported bookmarks with JSON output only
./bookmark_miner.py --file ~/Downloads/bookmarks-2024.json --format json

# Get markdown report without filtering
./bookmark_miner.py --source chrome --format markdown --output ./reports/
```

## Sample Output

### Markdown (project-ideas.md)
Shows categorized ideas with visual buildability bars:

```markdown
## TOOLS (3 ideas)

### 1. Markdown to HTML Converter CLI ✅
**Buildability:** `█████████░` (0.95)
**URL:** https://github.com/example/md-converter
**Concepts:** converter, markdown, github
**Reasoning:** Contains 2 easy-build indicators; Category is weekend-friendly; GitHub project
```

### JSON (project-ideas.json)
Structured data for further processing:

```json
{
  "generated_at": "2024-01-29T14:36:40",
  "total_ideas": 11,
  "weekend_feasible": 6,
  "ideas": [
    {
      "title": "Markdown to HTML Converter CLI",
      "url": "https://github.com/example/md-converter",
      "category": "tools",
      "concepts": ["converter", "markdown", "github"],
      "buildable_score": 0.95,
      "weekend_feasible": true,
      "reasoning": "Contains 2 easy-build indicators; Category is weekend-friendly; GitHub project"
    }
  ]
}
```

## Tips

- Use `--buildable` to filter noise and focus on achievable projects
- The `tools` and `web` categories tend to score highest for buildability
- GitHub URLs get bonus points (code references available)
- CLI/script/bot keywords boost buildability scores
- Complex/platform/enterprise keywords lower scores

#!/usr/bin/env python3
"""
bookmark-miner: Extract and analyze project ideas from browser bookmarks
"""

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse


@dataclass
class Bookmark:
    """Represents a single bookmark"""
    name: str
    url: str
    date_added: Optional[str] = None
    folder_path: str = ""
    
    def __post_init__(self):
        """Extract domain and clean name"""
        self.domain = urlparse(self.url).netloc
        self.clean_name = self._clean_name()
    
    def _clean_name(self) -> str:
        """Remove common junk from bookmark names"""
        # Remove trailing stuff like " - YouTube", " | GitHub", etc.
        cleaned = re.sub(r'\s*[-|]\s*[\w\s]+$', '', self.name)
        return cleaned.strip() or self.name


@dataclass
class ProjectIdea:
    """Represents an analyzed project idea from bookmarks"""
    title: str
    url: str
    category: str
    concepts: List[str]
    buildable_score: float  # 0-1 score
    weekend_feasible: bool
    reasoning: str
    source_bookmark: str
    

class BookmarkParser:
    """Parse Chrome/Firefox bookmarks"""
    
    @staticmethod
    def parse_chrome(bookmarks_file: str) -> List[Bookmark]:
        """Parse Chrome bookmarks JSON file"""
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bookmarks = []
        
        def traverse(node, path=""):
            """Recursively traverse bookmark tree"""
            if node.get('type') == 'url':
                # It's a bookmark
                bm = Bookmark(
                    name=node.get('name', 'Untitled'),
                    url=node.get('url', ''),
                    date_added=node.get('date_added'),
                    folder_path=path
                )
                bookmarks.append(bm)
            elif node.get('type') == 'folder':
                # It's a folder, recurse into children
                folder_name = node.get('name', 'Unnamed')
                new_path = f"{path}/{folder_name}" if path else folder_name
                for child in node.get('children', []):
                    traverse(child, new_path)
        
        # Chrome bookmarks have roots: bookmark_bar, other, synced
        roots = data.get('roots', {})
        for root_name, root_node in roots.items():
            if root_name in ['bookmark_bar', 'other', 'synced']:
                traverse(root_node, root_name)
        
        return bookmarks
    
    @staticmethod
    def find_chrome_bookmarks() -> Optional[str]:
        """Auto-detect Chrome bookmarks file location"""
        possible_paths = [
            "~/.config/google-chrome/Default/Bookmarks",
            "~/.config/chromium/Default/Bookmarks",
            "~/Library/Application Support/Google/Chrome/Default/Bookmarks",
            "~/AppData/Local/Google/Chrome/User Data/Default/Bookmarks",
        ]
        
        for path in possible_paths:
            expanded = Path(path).expanduser()
            if expanded.exists():
                return str(expanded)
        return None


class ProjectAnalyzer:
    """Analyze bookmarks for project ideas and buildability"""
    
    # Keyword-based categorization
    CATEGORIES = {
        'tools': ['tool', 'editor', 'IDE', 'cli', 'terminal', 'utility', 'app', 'software'],
        'saas': ['dashboard', 'platform', 'service', 'api', 'cloud', 'app', 'automation'],
        'games': ['game', 'unity', 'unreal', 'godot', 'phaser', 'pygame', 'engine'],
        'hardware': ['arduino', 'raspberry', 'pi', 'iot', 'sensor', 'esp32', 'microcontroller'],
        'web': ['html', 'css', 'javascript', 'react', 'vue', 'svelte', 'frontend', 'backend'],
        'ai_ml': ['ai', 'ml', 'machine learning', 'neural', 'gpt', 'llm', 'model', 'tensorflow'],
        'data': ['database', 'sql', 'nosql', 'analytics', 'visualization', 'dashboard'],
        'creative': ['design', 'art', 'music', 'video', 'generator', 'creator'],
        'dev_ops': ['docker', 'kubernetes', 'ci/cd', 'deploy', 'infrastructure', 'monitoring'],
        'mobile': ['ios', 'android', 'mobile', 'app', 'flutter', 'react native'],
    }
    
    # Buildability factors (higher = easier weekend project)
    EASY_INDICATORS = ['cli', 'script', 'bot', 'scraper', 'parser', 'converter', 'simple', 'basic']
    HARD_INDICATORS = ['platform', 'enterprise', 'scale', 'infrastructure', 'distributed', 'complex']
    
    def categorize(self, bookmark: Bookmark) -> str:
        """Determine category from bookmark content"""
        text = f"{bookmark.name} {bookmark.url} {bookmark.domain}".lower()
        
        scores = {}
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return 'other'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def extract_concepts(self, bookmark: Bookmark) -> List[str]:
        """Extract key concepts from bookmark"""
        concepts = []
        
        # Extract from name
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', bookmark.clean_name)
        concepts.extend(words[:5])  # Top 5 words
        
        # Extract from domain
        domain_parts = bookmark.domain.replace('www.', '').split('.')
        if domain_parts:
            concepts.append(domain_parts[0])
        
        # Deduplicate and clean
        concepts = list(set(c.lower() for c in concepts if len(c) > 3))
        return concepts[:8]  # Max 8 concepts
    
    def calculate_buildability(self, bookmark: Bookmark, category: str) -> tuple[float, str]:
        """Calculate buildability score (0-1) and reasoning"""
        text = f"{bookmark.name} {bookmark.url}".lower()
        score = 0.5  # Base score
        reasons = []
        
        # Check for easy indicators
        easy_count = sum(1 for ind in self.EASY_INDICATORS if ind in text)
        if easy_count > 0:
            score += 0.1 * easy_count
            reasons.append(f"Contains {easy_count} easy-build indicators")
        
        # Check for hard indicators
        hard_count = sum(1 for ind in self.HARD_INDICATORS if ind in text)
        if hard_count > 0:
            score -= 0.15 * hard_count
            reasons.append(f"Contains {hard_count} complex indicators")
        
        # Category-based adjustments
        if category in ['tools', 'cli', 'web']:
            score += 0.15
            reasons.append("Category is weekend-friendly")
        elif category in ['hardware', 'infrastructure', 'platform']:
            score -= 0.2
            reasons.append("Category typically requires more time")
        
        # GitHub repos are often buildable
        if 'github.com' in bookmark.url:
            score += 0.1
            reasons.append("GitHub project (likely has code reference)")
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        reasoning = "; ".join(reasons) if reasons else "Standard project complexity"
        
        return score, reasoning
    
    def analyze(self, bookmarks: List[Bookmark], buildable_only: bool = False) -> List[ProjectIdea]:
        """Analyze bookmarks and generate project ideas"""
        ideas = []
        
        for bm in bookmarks:
            category = self.categorize(bm)
            concepts = self.extract_concepts(bm)
            score, reasoning = self.calculate_buildability(bm, category)
            weekend_feasible = score >= 0.6
            
            if buildable_only and not weekend_feasible:
                continue
            
            idea = ProjectIdea(
                title=bm.clean_name,
                url=bm.url,
                category=category,
                concepts=concepts,
                buildable_score=score,
                weekend_feasible=weekend_feasible,
                reasoning=reasoning,
                source_bookmark=bm.name
            )
            ideas.append(idea)
        
        # Sort by buildability score (descending)
        ideas.sort(key=lambda x: x.buildable_score, reverse=True)
        
        return ideas


class OutputFormatter:
    """Format analysis results"""
    
    @staticmethod
    def to_json(ideas: List[ProjectIdea], output_file: str):
        """Save ideas as JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_ideas': len(ideas),
            'weekend_feasible': sum(1 for i in ideas if i.weekend_feasible),
            'ideas': [asdict(idea) for idea in ideas]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved JSON to {output_file}")
    
    @staticmethod
    def to_markdown(ideas: List[ProjectIdea], output_file: str):
        """Save ideas as readable Markdown"""
        lines = [
            "# Bookmark-Mined Project Ideas",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\n**Total Ideas:** {len(ideas)}",
            f"**Weekend-Feasible:** {sum(1 for i in ideas if i.weekend_feasible)}",
            "\n---\n"
        ]
        
        # Group by category
        by_category = {}
        for idea in ideas:
            by_category.setdefault(idea.category, []).append(idea)
        
        for category, cat_ideas in sorted(by_category.items()):
            lines.append(f"\n## {category.upper()} ({len(cat_ideas)} ideas)\n")
            
            for i, idea in enumerate(cat_ideas, 1):
                feasible_emoji = "✅" if idea.weekend_feasible else "⏰"
                score_bar = "█" * int(idea.buildable_score * 10) + "░" * (10 - int(idea.buildable_score * 10))
                
                lines.append(f"### {i}. {idea.title} {feasible_emoji}")
                lines.append(f"**Buildability:** `{score_bar}` ({idea.buildable_score:.2f})")
                lines.append(f"**URL:** {idea.url}")
                lines.append(f"**Concepts:** {', '.join(idea.concepts)}")
                lines.append(f"**Reasoning:** {idea.reasoning}")
                lines.append("")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ Saved Markdown to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract project ideas from browser bookmarks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Chrome bookmarks (auto-detected)
  bookmark-mine --source chrome
  
  # Only show weekend-buildable projects
  bookmark-mine --source chrome --buildable
  
  # Use custom bookmarks file
  bookmark-mine --file ~/my-bookmarks.json
  
  # Specify custom output directory
  bookmark-mine --source chrome --output ./ideas/
        """
    )
    
    parser.add_argument('--source', choices=['chrome', 'firefox'], 
                       help='Browser source (auto-detects bookmark location)')
    parser.add_argument('--file', type=str,
                       help='Path to bookmarks file (overrides --source)')
    parser.add_argument('--buildable', action='store_true',
                       help='Only show weekend-buildable projects (score >= 0.6)')
    parser.add_argument('--output', type=str, default='.',
                       help='Output directory for results (default: current dir)')
    parser.add_argument('--format', choices=['json', 'markdown', 'both'], default='both',
                       help='Output format (default: both)')
    
    args = parser.parse_args()
    
    # Determine bookmarks file
    bookmarks_file = None
    if args.file:
        bookmarks_file = args.file
    elif args.source == 'chrome':
        bookmarks_file = BookmarkParser.find_chrome_bookmarks()
        if not bookmarks_file:
            print("❌ Could not auto-detect Chrome bookmarks. Use --file to specify path.")
            return 1
    else:
        print("❌ Please specify --source or --file")
        parser.print_help()
        return 1
    
    if not os.path.exists(bookmarks_file):
        print(f"❌ Bookmarks file not found: {bookmarks_file}")
        return 1
    
    print(f"📚 Parsing bookmarks from: {bookmarks_file}")
    
    # Parse bookmarks
    bookmarks = BookmarkParser.parse_chrome(bookmarks_file)
    print(f"✓ Found {len(bookmarks)} bookmarks")
    
    # Analyze
    print(f"🔍 Analyzing for project ideas...")
    analyzer = ProjectAnalyzer()
    ideas = analyzer.analyze(bookmarks, buildable_only=args.buildable)
    print(f"✓ Generated {len(ideas)} project ideas")
    
    if args.buildable:
        weekend_count = len(ideas)  # All are weekend-feasible if filtered
    else:
        weekend_count = sum(1 for i in ideas if i.weekend_feasible)
    print(f"✅ {weekend_count} are weekend-feasible")
    
    # Output results
    os.makedirs(args.output, exist_ok=True)
    
    if args.format in ['json', 'both']:
        json_file = os.path.join(args.output, 'project-ideas.json')
        OutputFormatter.to_json(ideas, json_file)
    
    if args.format in ['markdown', 'both']:
        md_file = os.path.join(args.output, 'project-ideas.md')
        OutputFormatter.to_markdown(ideas, md_file)
    
    print("\n🎉 Done! Happy building!")
    return 0


if __name__ == '__main__':
    exit(main())

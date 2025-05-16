import sqlite3
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict
import rich
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.logging import RichHandler
import logging
from dataclasses import dataclass

DATABASES_FILENAME = "plugins.db"
logger = logging.getLogger(__name__)

@dataclass
class IdaPlugin:
    repository: str
    parent: str | None
    description: str
    file: str
    url: str
    content: str
    wanted_name: str | None
    comment: str | None
    created_at: datetime
    pushed_at: datetime
    forks_count: int
    stargazers_count: int

def load_plugin(row: tuple) -> IdaPlugin:
    return IdaPlugin(
        repository=row[0],
        file=row[1],
        parent=row[2],
        description=row[3],
        url=row[4],
        content=row[5],
        wanted_name=row[6],
        comment=row[7],
        created_at=datetime.fromisoformat(row[8]),
        pushed_at=datetime.fromisoformat(row[9]),
        forks_count=row[10],
        stargazers_count=row[11]
    )

def timeline_plugins(db_path: Path) -> None:
    events_by_day: dict[str, list[tuple[IdaPlugin, str]]] = defaultdict(list)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT * FROM plugins")
        for row in cursor:
            plugin = load_plugin(row)
            for ts, label in ((plugin.created_at, "created"), (plugin.pushed_at, "pushed")):
                events_by_day[str(ts.date())].append((plugin, label))

    def humanize_days_ago(day_str: str) -> str:
        today = date.today()
        d = datetime.fromisoformat(day_str).date()
        delta = (today - d).days
        if delta == 0:
            return "today"
        if delta == 1:
            return "yesterday"
        if delta < 7:
            return f"{delta} days ago"
        if delta < 30:
            weeks = delta // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        months = delta // 30
        return f"{months} month{'s' if months > 1 else ''} ago"

    t = Table(show_header=False, box=None, padding=(0, 0, 0, 0))
    t.add_column("Repository", style="cyan", no_wrap=True)
    t.add_column("File", style="white")
    t.add_column("Stars", style="yellow", justify="right")
    t.add_column("Forks", style="green", justify="right")

    last_day = None
    for day in sorted(events_by_day.keys(), reverse=True):
        if humanize_days_ago(day) != last_day:
            t.add_row(Text(humanize_days_ago(day), style="yellow"))
            last_day = humanize_days_ago(day)

        for plugin, label in events_by_day[day]:
            if plugin.repository in ("clovme/WTools",):
                continue
            t.add_row(
                "  " + plugin.repository + (" [grey69](created)[/grey69]" if label == "created" else ""),
                plugin.file, 
                f"{plugin.stargazers_count} [grey69]stars[/grey69]", 
                f"  {plugin.forks_count} [grey69]forks[/grey69]"
            )

    rich.print(t)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Show plugin activity timeline for last 3 months")
    parser.add_argument("path", type=Path, help="Path to directory containing database and repos")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )
    timeline_plugins(args.path / DATABASES_FILENAME)

if __name__ == "__main__":
    main() 
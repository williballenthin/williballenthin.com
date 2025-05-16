# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/github-ida-plugins/show-github-ida-plugins.py \
#       content/posts/2025-05-15-github-ida-plugins/
#
# /// script
# dependencies = [
#    "rich>=14.0.0",
#    "jinja2>=3.1.0",
# ]
# ///
import sqlite3
from pathlib import Path
from datetime import datetime
import rich
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.logging import RichHandler
import logging
from dataclasses import dataclass
from jinja2 import Template

DATABASES_FILENAME = "plugins.db"
logger = logging.getLogger(__name__)

# we put the styles first because the body content can be pretty large (hundreds of KBs)
# which takes a moment to load.
PLUGIN_TEMPLATE = """
<style>
    #plugins.has-js thead {
        display: none;
    }

    #plugins tr td,
    table tr td {
        padding: 0;
        padding-top: 0.5em;
        vertical-align: top;
    }

    table tr td:nth-last-child(1) {
        text-align: right;
    }

    #plugins.no-js tr td:nth-last-child(1),
    #plugins.no-js tr td:nth-last-child(2),
    #plugins.no-js tr td:nth-last-child(3),
    #plugins.no-js tr td:nth-last-child(4),
    #plugins.no-js thead th:nth-last-child(1),
    #plugins.no-js thead th:nth-last-child(2),
    #plugins.no-js thead th:nth-last-child(3),
    #plugins.no-js thead th:nth-last-child(4) {
        display: none;
    }

    #sort-links.no-js {
        display: none;
    }
</style>

<div id="sort-links" class="no-js">
  <span>Sort by:</span>
  <a href="#" id="sort-repo">repo</a>
  <a href="#" id="sort-stars">stars</a>
  <a href="#" id="sort-forks">forks</a>
  <a href="#" id="sort-created">created</a>
  <a href="#" id="sort-pushed">pushed</a>*
</div>

<table id="plugins" class="no-js" style="table-layout: fixed; width: 100%;">
<thead>
    <tr>
        <th></th>
        <th width="100px"></th>
        <th>stars</th>
        <th>forks</th>
        <th>created</th>
        <th>pushed</th>
    </tr>
</thead>
<tbody>
    {% for plugin in plugins %}
  <tr>
    <td>
      <p>
        <b>
            <a class="contrast" href="https://www.github.com/{{ plugin.repository }}">
            {{ plugin.repository }}
            </a>
        </b>
        :: 
        <a 
            href="{{ plugin.url }}" 
            {% if plugin.wanted_name or plugin.comment %}
                data-tooltip="
                    {% if plugin.wanted_name and plugin.comment %}
                        {{ plugin.wanted_name }}: {{ plugin.comment }}
                    {% elif plugin.wanted_name %}
                        {{ plugin.wanted_name }}
                    {% elif plugin.comment %}
                        {{ plugin.comment }}
                    {% endif %}
                "
            {% endif %}
            >{{ plugin.file }}</a>
      </p>
      {% if plugin.description %}
        <p>
          {{ plugin.description }}
        </p>
      {% endif %}
    </td>
    <td>
        {{ plugin.stargazers_count }} <span class="decoration">stars</span><br />
        {{ plugin.forks_count }} <span class="decoration">forks</span><br />
        {% if plugin.created_at.year != plugin.pushed_at.year %}
            <span class="decoration">{{ plugin.created_at.year }}→{{ plugin.pushed_at.year - 2000 }}</span>
        {% else %}
            <span class="decoration">{{ plugin.created_at.year }}</span>
        {% endif %}
    </td>
    <td>{{plugin.stargazers_count}}</td>
    <td>{{plugin.forks_count}}</td>
    <td>{{plugin.created_at.date()}}</td>
    <td>{{plugin.pushed_at.date()}}</td>
  </tr>
  {% endfor %}
  </tbody>
</table>
<p class='feed-metadata-generated'>generated: {{now.strftime('%B %d, %Y at %H:%M:%S')}}</p>

<script src="/js/jquery-3.7.1.js"></script>
<link rel="stylesheet" type="text/css" href="/css/dataTables.dataTables.min.css">
<script src="/js/dataTables.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const dt = new DataTable('#plugins', {
            pageLength: -1,
            layout: {
                topStart: null,
                topEnd: null,
                bottomStart: null,
                bottomEnd: null,
            },
            columnDefs: [
                { width: '100px', targets: 1 },
                { visible: false, targets: [2,3,4,5] }
            ],
            order: [[5, 'desc']],
        });

        $(".no-js").removeClass("no-js");
        $("#plugins").addClass("has-js");

        $('#sort-repo').click(function() {
            dt.column(0).order('asc').draw();
        });
        $('#sort-stars').click(function() {
            dt.column(2).order('desc').draw();
        });
        $('#sort-forks').click(function() {
            dt.column(3).order('desc').draw();
        });
        $('#sort-created').click(function() {
            dt.column(4).order('desc').draw();
        });
        $('#sort-pushed').click(function() {
            dt.column(5).order('desc').draw();
        });
    });
</script>
"""


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


def render_plugins_console(plugins: list[IdaPlugin]) -> None:
    for plugin in plugins:
        table = Table(show_header=False, width=120)
        table.add_column("Property", style="grey69", width=15)
        table.add_column("Value", width=105)

        t = Table(show_header=False, width=100, box=None, padding=(0, 0, 0, 0))
        t.add_column("name", width=70, style="bold yellow")
        t.add_column(width=1, style="grey69")
        t.add_column("stars", width=12)
        t.add_column(width=1, style="grey69")
        t.add_column("forks", width=10)
        t.add_row(
            plugin.repository + (f" (from {plugin.parent})" if plugin.parent else ""),
            " ",
            f"[yellow]{plugin.stargazers_count}[/yellow] [grey69]stars[/grey69]",
            " ",
            f" [yellow]{plugin.forks_count}[/yellow] [grey69]forks[/grey69]",
        )
        table.add_row("Repository", t)

        t = Table(show_header=False, width=100, box=None, padding=(0, 0, 0, 0))
        t.add_column("file", width=70)
        t.add_column(width=1, style="grey69")
        t.add_column("created", width=10)
        t.add_column(width=3, style="grey69")
        t.add_column("pushed", width=10)
        t.add_row(f"[link={plugin.url}]{plugin.file}[/link]", " ", str(plugin.created_at.date()), " → ", str(plugin.pushed_at.date()))
        table.add_row("File", t)

        if plugin.wanted_name:
            table.add_row("Plugin Name", plugin.wanted_name)
        if plugin.comment:
            table.add_row("Plugin Cmt", plugin.comment)
        table.add_row("Repo Descr", plugin.description or "N/A")

        rich.print(table)


def render_plugins_html(plugins: list[IdaPlugin]) -> None:
    now = datetime.now()
    template = Template(PLUGIN_TEMPLATE)
    print(template.render(plugins=plugins, now=now))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Display plugins from database")
    parser.add_argument("path", type=Path, help="Path to directory containing database and repos")
    parser.add_argument("--html", action="store_true", help="Output in HTML format")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )

    db_path = args.path / DATABASES_FILENAME
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT * FROM plugins")
        plugins = [load_plugin(row) for row in cursor]
        if args.html:
            render_plugins_html(plugins)
        else:
            render_plugins_console(plugins)


if __name__ == "__main__":
    main() 

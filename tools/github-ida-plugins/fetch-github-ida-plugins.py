# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/github-ida-plugins/fetch-github-ida-plugins.py \
#       > static/fragments/github-ida-plugins/list.html
#
# /// script
# dependencies = [
#    "rich>=13.0.0",
#    "pygithub>=2.6.1",
#    "tree-sitter>=0.24.0",
#    "tree-sitter-python>=0.23.6",
#    "jinja2>=3.1.0",
# ]
# ///
#
# requires env variable GITHUB_TOKEN to be set.
import os
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import urlparse

import tree_sitter_python as tspython
from github import Auth, Github
from jinja2 import Template
from tree_sitter import Parser, Language
from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

PY_LANGUAGE = Language(tspython.language())
PY_PARSER = Parser(PY_LANGUAGE)

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
    parent: str | None  # parent repository if it's a fork
    description: str
    file: str
    url: str
    wanted_name: str | None
    comment: str | None
    created_at: datetime
    pushed_at: datetime
    forks_count: int
    stargazers_count: int


def extract_repo_info(repo_input: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL or owner/repo format."""
    if repo_input.startswith(("http://", "https://")):
        path = urlparse(repo_input).path.strip("/")
        owner, repo = path.split("/")[:2]
    else:
        owner, repo = repo_input.split("/")
    return owner, repo


def extract_plugin_info(py_source: str) -> dict[str, str]:
    tree = PY_PARSER.parse(bytes(py_source, "utf-8"))
    # search for classes with class variables that are strings
    query = PY_LANGUAGE.query(
        """
        (class_definition
            body: (block
                    (expression_statement
                        (assignment
                            left: (identifier) @prop_name
                            right: (string) @prop_value
                        )
                    )
                  )
        )
    """
    )
    matches = query.captures(tree.root_node)

    props = {}
    for nodes in matches.values():
        for node in nodes:
            prop_name = node.parent.child_by_field_name("left").text.decode("utf-8")
            prop_value = node.parent.child_by_field_name("right").text.decode("utf-8").strip('"').strip("'")
            props[prop_name] = prop_value

    return props


def search_and_render_plugins(limit: int | None = None) -> None:
    """Search for IDA plugins on GitHub and render HTML directly."""
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
    g = Github(auth=auth)

    query = 'language:python AND "def PLUGIN_ENTRY()" AND in:file'
    logger.info("query: %s", query)

    results = g.search_code(query=query)
    logger.info("found %d IDA plugins", results.totalCount)

    plugins = []
    max_results = limit or results.totalCount

    for result in results[:max_results]:
        parent: str | None = None
        if result.repository.fork:
            if result.repository.parent:
                parent = result.repository.parent.full_name

        content = result.decoded_content.decode("utf-8")
        if "ida" not in content:
            logger.debug("skipping %s: no ida", result.html_url)
            continue

        if result.repository.full_name in ("clovme/WTools",):
            # these are handpicked repos to ignore
            # due to embedding the IDA SDK/example plugins
            logger.debug("skipping %s: denylist", result.html_url)
            continue

        props = extract_plugin_info(content)

        plugin = IdaPlugin(
            repository=result.repository.full_name,
            parent=parent,
            description=result.repository.description,
            file=result.path,
            url=result.html_url,
            wanted_name=props.get("wanted_name"),
            comment=props.get("comment"),
            created_at=result.repository.created_at,
            pushed_at=result.repository.pushed_at,
            forks_count=result.repository.forks_count,
            stargazers_count=result.repository.stargazers_count,
        )
        plugins.append(plugin)
        logger.info("Found plugin: %s", plugin.repository)

    # Render HTML
    now = datetime.now()
    template = Template(PLUGIN_TEMPLATE)
    print(template.render(plugins=plugins, now=now))


def search_and_render_plugins_json(limit: int | None = None) -> None:
    """Search for IDA plugins on GitHub and output JSONL (one JSON object per line)."""

    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
    g = Github(auth=auth)

    query = 'language:python AND "def PLUGIN_ENTRY()" AND in:file'
    logger.info("query: %s", query)

    results = g.search_code(query=query)
    logger.info("found %d IDA plugins", results.totalCount)

    max_results = limit or results.totalCount

    for result in results[:max_results]:
        parent: str | None = None
        if result.repository.fork:
            if result.repository.parent:
                parent = result.repository.parent.full_name

        content = result.decoded_content.decode("utf-8")
        if "ida" not in content:
            logger.debug("skipping %s: no ida", result.html_url)
            continue

        if result.repository.full_name in ("clovme/WTools",):
            # these are handpicked repos to ignore
            # due to embedding the IDA SDK/example plugins
            logger.debug("skipping %s: denylist", result.html_url)
            continue

        props = extract_plugin_info(content)

        plugin = {
            "repository": result.repository.full_name,
            "parent": parent,
            "description": result.repository.description,
            "file": result.path,
            "url": result.html_url,
            "wanted_name": props.get("wanted_name"),
            "comment": props.get("comment"),
            "created_at": result.repository.created_at.isoformat(),
            "pushed_at": result.repository.pushed_at.isoformat(),
            "forks_count": result.repository.forks_count,
            "stargazers_count": result.repository.stargazers_count,
        }
        print(json.dumps(plugin))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find IDA Pro plugins on GitHub and generate HTML")
    parser.add_argument("--limit", type=int, help="Limit the number of results")
    parser.add_argument(
        "--json", action="store_true", help="Output as JSONL instead of HTML (one JSON object per line)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(console=Console(stderr=True))],
    )

    if args.json:
        search_and_render_plugins_json(args.limit)
    else:
        search_and_render_plugins(args.limit)


if __name__ == "__main__":
    main()

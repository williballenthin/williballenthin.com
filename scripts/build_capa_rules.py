#!/usr/bin/env python
"""
build the capa-rules website source for Hugo
"""
import os
import sys
import logging
import argparse
from pathlib import Path

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


logger = logging.getLogger(__name__)


def get_rule_terms(rule):
    features = rule["rule"]["features"]
    print(features)

    terms = set()
    def rec(node):
        match node:
            case {"or": children}:
                return list(map(rec, children))
            case {"and": children}:
                return list(map(rec, children))
            case {"not": children}:
                return list(map(rec, children))
            case {"optional": children}:
                return list(map(rec, children))
            case {"function": children}:
                return list(map(rec, children))
            case {"basic block": children}:
                return list(map(rec, children))
            case {"instruction": children}:
                return list(map(rec, children))
            case {"api": api}:
                terms.add(("api", api))
            case {"number": number}:
                terms.add(("number", number))
            case {"offset": offset}:
                terms.add(("offset", offset))
            case {"string": string}:
                terms.add(("string", string))
            case {"substring": substring}:
                terms.add(("substring", substring))
            case {"bytes": bytes_}:
                terms.add(("bytes", bytes_))
            case {"function-name": name}:
                terms.add(("function-name", name))
            case {"mnemonic": mnemonic}:
                terms.add(("mnemonic", mnemonic))
            case {"section": section}:
                terms.add(("section", section))
            case {"import": import_}:
                terms.add(("import", import_))
            case {"export": export}:
                terms.add(("export", export))
            case {"os": os}:
                terms.add(("os", os))
            case {"arch": arch}:
                terms.add(("arch", arch))
            case {"format": format}:
                terms.add(("format", format))
            case {"class": class_}:
                terms.add(("class", class_))
            case {"namespace": namespace}:
                terms.add(("namespace", namespace))
            case {"property/read": property_}:
                terms.add(("property", property_))
            case {"property/write": property_}:
                terms.add(("property", property_))
            case {"match": match_}:
                terms.add(("match", match_))
            case {"characteristic": characteristic}:
                terms.add(("characteristic", characteristic))
            case {"description": _}:
                return
            case _:
                key = list(node.keys())[0]
                if key.endswith("or more"):
                    return list(map(rec, node[key]))
                elif key.endswith("].number"):
                    terms.add(("number", node[key]))
                elif key.endswith("].offset"):
                    terms.add(("offset", node[key]))
                elif key.startswith("count("):
                    # skip for now
                    return
                else:
                    raise NotImplementedError(node)

    assert isinstance(features, list)
    for node in features:
        rec(node)

    return terms


def build_capa_rule(rule_path: Path, site_path: Path) -> None:
    rule_id = rule_path.stem
    rule = yaml.load(rule_path.read_text(), Loader=Loader)

    rule_name = rule["rule"]["meta"]["name"]
    namespace = rule["rule"]["meta"].get("namespace")
    authors = rule["rule"]["meta"]["authors"]

    # danger: injection throughout here.
    lines = []
    lines.append("---")
    lines.append(f"title: '{rule_name}'")
    lines.append(f"slug: {rule_id}")

    # metadata: nursery
    lines.append(f"nursery: {'/nursery/' in rule_path.as_posix()}")

    # metadata: lib
    lines.append(f"lib: {rule['rule']['meta'].get('lib', False)}")

    # metadata: scope
    lines.append(f"scope: {rule['rule']['meta']['scope']}")

    # taxonomoy: authors
    lines.append("authors:")
    for author in authors:
        lines.append(f"  - '{author}'")

    lines.append("namespaces:")
    if namespace:
        # taxonomoy: namespaces
        lines.append(f"  - '{namespace}'")

    # metadata: namespace
    lines.append(f"namespace: {namespace or 'xxx'}")

    # taxonomoy: attack
    lines.append("attack:")
    for attack in rule["rule"]["meta"].get("att&ck", []):
        lines.append(f"  - '{attack}'")

    # taxonomoy: mbc
    lines.append("mbc:")
    for mbc in rule["rule"]["meta"].get("mbc", []):
        lines.append(f"  - '{mbc}'")

    # metadata: references
    lines.append("references:")
    for reference in rule["rule"]["meta"].get("references", []):
        lines.append(f"  - '{reference}'")

    # metadata: examples
    lines.append("examples:")
    for example in rule["rule"]["meta"].get("examples", []):
        lines.append(f"  - '{example}'")

    # metadata: description
    description = rule["rule"]["meta"].get("description", "").strip()
    if description:
        lines.append(f"description: {yaml.dump(description, Dumper=Dumper)}")

    lines.append("api:")
    for v in [v for k, v in get_rule_terms(rule) if k == "api"]:
        v = v.replace("'", "\\'")
        lines.append(f"  - '{v}'")

    lines.append("---")
    lines.append("```yaml")
    lines.append(rule_path.read_text().partition("features:\n")[2])
    lines.append("```")

    rule_site_path = site_path / "content" / "rules" / (rule_id + ".md")
    rule_site_path.write_text("\n".join(lines))



def build_capa_rules(rules_path: Path, site_path: Path) -> None:
    (site_path / "content" / "rules").mkdir(exist_ok=True, parents=True)

    for base, _, filenames in os.walk(rules_path):
        for filename in filenames:
            if not filename.endswith(".yml"):
                continue
            if ".git" in base:
                continue

            rule_path = Path(os.path.join(base, filename))
            logger.info("processing rule: %s", rule_path.relative_to(rules_path))

            build_capa_rule(rule_path, site_path)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="A program.")
    parser.add_argument("input", type=str,
                        help="Path to capa-rules repository")
    parser.add_argument("output", type=str,
                        help="Path to Hugo site")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Disable all output but errors")
    args = parser.parse_args(args=argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger().setLevel(logging.INFO)

    rules_path = Path(args.input)
    site_path = Path(args.output)

    build_capa_rules(rules_path, site_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
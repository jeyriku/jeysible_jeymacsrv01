#!/usr/bin/env python3
"""parse_show_version.py
Simple parser for Cisco `show version` output. Writes JSON and YAML (if PyYAML present).
Usage: parse_show_version.py <input_file> <output_prefix>
"""
import sys
import re
import json
from pathlib import Path


def parse_show_version(text):
    data = {}

    # hostname from prompt (last line like hostname#)
    m = re.search(r"(?m)^([A-Za-z0-9_\-]+)[#>]\\s*$", text)
    if m:
        data['hostname'] = m.group(1)

    # IOS version
    m = re.search(r"Version\s+([\d\.A-Za-z\-\(\)]+)", text)
    if m:
        data['version'] = m.group(1)

    # model / platform
    m = re.search(r"^\s*cisco\s+(\S+)\s+.*bytes of memory", text, re.IGNORECASE | re.MULTILINE)
    if m:
        data['model'] = m.group(1)
    else:
        m = re.search(r"^\s*Model number\s*:\s*(\S+)", text, re.IGNORECASE | re.MULTILINE)
        if m:
            data['model'] = m.group(1)

    # serial number
    m = re.search(r"Processor board ID\s+(\S+)", text)
    if m:
        data['serial'] = m.group(1)
    else:
        m = re.search(r"System serial number\s*:\s*(\S+)", text, re.IGNORECASE)
        if m:
            data['serial'] = m.group(1)

    data['raw'] = text
    return data


def main():
    if len(sys.argv) < 3:
        print("Usage: parse_show_version.py <input_file> <output_prefix>")
        sys.exit(2)

    infile = Path(sys.argv[1])
    prefix = Path(sys.argv[2])
    if not infile.exists():
        print(f"Input file not found: {infile}")
        sys.exit(3)

    text = infile.read_text(encoding='utf-8', errors='ignore')
    parsed = parse_show_version(text)

    # write json
    json_path = prefix.with_suffix('.json')
    json_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding='utf-8')

    # try to write yaml if pyyaml available
    try:
        import yaml
        yaml_path = prefix.with_suffix('.yml')
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(parsed, f, default_flow_style=False, allow_unicode=True)
    except Exception:
        # ignore if pyyaml not installed
        pass

    print(f"Wrote: {json_path}")


if __name__ == '__main__':
    main()

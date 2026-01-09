#!/usr/bin/env python3
"""parse_show_version_pyats.py
Parse 'show version' using PyATS/Genie if available and write JSON/YAML outputs.
Usage: parse_show_version_pyats.py <input_file> <output_prefix>
"""
import sys
from pathlib import Path
import json

def main():
    if len(sys.argv) < 3:
        print("Usage: parse_show_version_pyats.py <input_file> <output_prefix>")
        return 2

    infile = Path(sys.argv[1])
    prefix = Path(sys.argv[2])
    if not infile.exists():
        print(f"Input file not found: {infile}")
        return 3

    text = infile.read_text(encoding='utf-8', errors='ignore')

    try:
        # Try to import Genie parser utilities
        from genie.libs.parser.utils import get_parser
        # get_parser(command, platform) -> parser class instance
        parser = get_parser('show version', 'ios')
        # some parser instances accept `parse()` with text kwarg
        try:
            parsed = parser.parse(text=text)
        except TypeError:
            # fallback: many parsers implement parse with **kwargs
            parsed = parser.parse(output=text)
    except Exception as exc:
        # If Genie not available or parsing fails, fallback to basic extraction
        parsed = {
            'parse_error': str(exc),
            'raw': text
        }

    # write json
    json_path = prefix.with_suffix('.json')
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding='utf-8')

    # try yaml
    try:
        import yaml
        yaml_path = prefix.with_suffix('.yml')
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(parsed, f, default_flow_style=False, allow_unicode=True)
    except Exception:
        pass

    print(f"Wrote: {json_path}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
#!/usr/bin/env python3
"""Stub PyATS parser for `show version`.
Attempts to import Genie/PyATS and parse if available; otherwise prints an instruction.
Usage: parse_show_version_pyats.py <input_file> <output_prefix>
"""
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: parse_show_version_pyats.py <input_file> <output_prefix>")
        return 2

    infile = Path(sys.argv[1])
    prefix = Path(sys.argv[2])
    if not infile.exists():
        print(f"Input file not found: {infile}")
        return 3

    try:
        # Try to import genie/pyats
        import genie
        from genie.libs.parser.utils import get_parser
    except Exception:
        print("PyATS/Genie not installed in this environment.")
        print("To enable PyATS parsing, install it in your venv: pip install pyats genieparser")
        return 4

    text = infile.read_text(encoding='utf-8', errors='ignore')

    # Note: implementing full genie parser usage is environment-specific.
    # This stub simply writes the raw input to json/yaml with a marker that PyATS is available.
    parsed = {'pyats_available': True, 'raw': text}

    import json
    json_path = prefix.with_suffix('.json')
    json_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote stub PyATS output: {json_path}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

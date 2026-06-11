#!/usr/bin/env python3
"""Generate register random configuration from reg_data.h and selection JSON.

The tool parses all registers under t_reg_vcpi from reg_data.h, filters active
registers via register_selection.json, generates random values, then writes cmd.cfg.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ERR_SELECTION_FILE_MISSING = "E_SELECTION_FILE_MISSING"
ERR_SELECTION_JSON_INVALID = "E_SELECTION_JSON_INVALID"
ERR_SELECTION_SCHEMA_INVALID = "E_SELECTION_SCHEMA_INVALID"
ERR_SELECTION_TARGET_NOT_FOUND = "E_SELECTION_TARGET_NOT_FOUND"
ERR_SELECTION_EMPTY_ACTIVE_SET = "E_SELECTION_EMPTY_ACTIVE_SET"
ERR_HEADER_STRUCT_NOT_FOUND = "E_HEADER_STRUCT_NOT_FOUND"

SPECIAL_CONSTRAINTS = {
    "VCPI_PIC_SIZE": {
        "ve_pic_width": (2, 1920, 2),
        "ve_pic_height": (2, 1080, 2),
    }
}


@dataclass(frozen=True)
class BitFieldDef:
    register_name: str
    name: str
    width: int


@dataclass(frozen=True)
class RegisterSelection:
    name: str
    enabled: bool
    source_index: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate cmd.cfg from register selection")
    parser.add_argument("--header", default="reg_data.h", help="Path to reg_data.h")
    parser.add_argument(
        "--select-json",
        default="register_selection.json",
        help="Path to register_selection.json",
    )
    parser.add_argument("--out", default="cmd.cfg", help="Output cfg file path")
    parser.add_argument("--seed", type=int, default=None, help="Optional RNG seed")
    parser.add_argument(
        "--dump-registers",
        action="store_true",
        help="Print parsed register and field catalog then exit",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def create_rng(seed: Optional[int]) -> random.Random:
    """Create a deterministic RNG instance for reproducible runs."""
    return random.Random(seed)


def parse_struct_definitions(header_text: str) -> Dict[str, str]:
    """Return mapping of typedef name -> struct body text."""
    pattern = re.compile(
        r"typedef\s+struct\s+\w*\s*\{(?P<body>.*?)\}\s*(?P<name>\w+)\s*;",
        re.DOTALL,
    )
    result: Dict[str, str] = {}
    for match in pattern.finditer(header_text):
        result[match.group("name")] = match.group("body")
    return result


def parse_bitfields(struct_body: str, register_name: str) -> List[BitFieldDef]:
    fields: List[BitFieldDef] = []
    pattern = re.compile(r"REG32\s+(?P<name>\w+)\s*:\s*(?P<width>\d+)")
    for match in pattern.finditer(struct_body):
        field_name = match.group("name")
        if field_name.lower().startswith("rsvd"):
            continue
        fields.append(
            BitFieldDef(
                register_name=register_name,
                name=field_name,
                width=int(match.group("width")),
            )
        )
    return fields


def parse_vcpi_member_order(vcpi_struct_body: str) -> List[Tuple[str, str]]:
    """Return ordered tuples of (register_name, typedef_name) under t_reg_vcpi."""
    members: List[Tuple[str, str]] = []
    line_pattern = re.compile(
        r"(?P<typedef>t_reg_\w+)\s+(?P<member>VCPI_[A-Z0-9_]+)(?:\s*\[\d+\])?\s*;"
    )
    for line in vcpi_struct_body.splitlines():
        match = line_pattern.search(line)
        if match:
            members.append((match.group("member"), match.group("typedef")))
    return members


def build_register_catalog(header_text: str) -> Dict[str, List[BitFieldDef]]:
    structs = parse_struct_definitions(header_text)
    if "typedef struct" in header_text and not structs:
        raise ValueError(
            f"{ERR_HEADER_STRUCT_NOT_FOUND}: no typedef struct block parsed from reg_data.h"
        )

    vcpi_body = structs.get("t_reg_vcpi")
    if not vcpi_body:
        raise ValueError(f"{ERR_HEADER_STRUCT_NOT_FOUND}: t_reg_vcpi not found in header")

    alias_pattern = re.compile(r"typedef\s+uint32_t\s+(?P<name>\w+)\s*;")
    scalar_aliases = {m.group("name") for m in alias_pattern.finditer(header_text)}

    catalog: Dict[str, List[BitFieldDef]] = {}
    for register_name, typedef_name in parse_vcpi_member_order(vcpi_body):
        body = structs.get(typedef_name)
        if not body:
            if typedef_name in scalar_aliases:
                # Scalar typedef registers are represented as empty bitfield lists.
                catalog[register_name] = []
            continue
        fields = parse_bitfields(body, register_name)
        catalog[register_name] = fields

    return catalog


def parse_selection_json(select_path: Path) -> List[RegisterSelection]:
    if not select_path.exists():
        raise FileNotFoundError(f"{ERR_SELECTION_FILE_MISSING}: {select_path}")

    try:
        data = json.loads(select_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{ERR_SELECTION_JSON_INVALID}: {exc.msg}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("registers"), list):
        raise ValueError(
            f"{ERR_SELECTION_SCHEMA_INVALID}: root must contain list field 'registers'"
        )

    selections: List[RegisterSelection] = []
    for index, item in enumerate(data["registers"]):
        if not isinstance(item, dict):
            raise ValueError(
                f"{ERR_SELECTION_SCHEMA_INVALID}: registers[{index}] must be object"
            )

        name = item.get("name")
        enabled = item.get("enabled")
        if not isinstance(name, str) or not isinstance(enabled, bool):
            raise ValueError(
                f"{ERR_SELECTION_SCHEMA_INVALID}: registers[{index}] requires name(str), enabled(bool)"
            )
        selections.append(RegisterSelection(name=name, enabled=enabled, source_index=index))

    return selections


def resolve_active_targets(
    selections: List[RegisterSelection],
    catalog: Dict[str, List[BitFieldDef]],
) -> List[str]:
    status_by_name: Dict[str, bool] = {}
    for selection in selections:
        if selection.name not in catalog:
            raise ValueError(
                f"{ERR_SELECTION_TARGET_NOT_FOUND}: {selection.name} at index {selection.source_index}"
            )
        status_by_name[selection.name] = selection.enabled

    targets = [name for name in catalog.keys() if status_by_name.get(name, False)]
    if not targets:
        raise ValueError(ERR_SELECTION_EMPTY_ACTIVE_SET)
    return targets


def pick_aligned(rng: random.Random, min_value: int, max_value: int, align: int) -> int:
    if align <= 1:
        return rng.randint(min_value, max_value)

    start = min_value + ((align - (min_value % align)) % align)
    if start > max_value:
        raise ValueError("E_VALUE_RANGE_INVALID: no aligned value in range")
    count = ((max_value - start) // align) + 1
    return start + align * rng.randrange(count)


def generate_field_value(
    rng: random.Random,
    register_name: str,
    field_name: str,
    width: int,
) -> int:
    max_from_width = (1 << width) - 1

    min_value = 0
    max_value = max_from_width
    align = 1
    reg_constraints = SPECIAL_CONSTRAINTS.get(register_name, {})
    if field_name in reg_constraints:
        min_value, max_value, align = reg_constraints[field_name]
        max_value = min(max_value, max_from_width)

    return pick_aligned(rng, min_value, max_value, align)


def generate_values(
    targets: Iterable[str],
    catalog: Dict[str, List[BitFieldDef]],
    seed: Optional[int],
) -> Tuple[Dict[str, List[Tuple[str, int]]], Dict[str, object]]:
    rng = create_rng(seed)

    generated: Dict[str, List[Tuple[str, int]]] = {}
    applied_rule_mode: Dict[str, str] = {}
    metadata: Dict[str, object] = {"seed": seed, "applied_rule_mode": applied_rule_mode}
    for register_name in targets:
        fields = catalog.get(register_name)
        if fields is None:
            raise ValueError(f"{ERR_SELECTION_TARGET_NOT_FOUND}: register {register_name}")

        values: List[Tuple[str, int]] = []
        if not fields:
            value = generate_field_value(rng, register_name, register_name.lower(), 32)
            values.append((register_name.lower(), value))
            applied_rule_mode[f"{register_name}.{register_name.lower()}"] = "FULL_RANDOM"
            generated[register_name] = values
            continue

        for field in fields:
            value = generate_field_value(rng, register_name, field.name, field.width)
            values.append((field.name, value))
            applied_rule_mode[f"{register_name}.{field.name}"] = "FULL_RANDOM"
        generated[register_name] = values

    return generated, metadata


def format_cfg(generated: Dict[str, List[Tuple[str, int]]]) -> str:
    lines: List[str] = []
    for register_name, fields in generated.items():
        tail = "===================="
        lines.append(f"#================ {register_name} {tail}")
        for field_name, value in fields:
            lines.append(f"{field_name:<48}: {value}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False, dir=str(path.parent)
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def dump_registers(catalog: Dict[str, List[BitFieldDef]]) -> None:
    for register_name, fields in catalog.items():
        print(register_name)
        if not fields:
            print("  - (scalar)")
            continue
        for field in fields:
            print(f"  - {field.name} ({field.width})")


def count_catalog(catalog: Dict[str, List[BitFieldDef]]) -> Tuple[int, int]:
    return len(catalog), sum(len(fields) for fields in catalog.values())


def main() -> int:
    args = parse_args()
    try:
        header_text = read_text(Path(args.header))
        catalog = build_register_catalog(header_text)
        register_count, field_count = count_catalog(catalog)

        if args.dump_registers:
            dump_registers(catalog)
            print(f"Parsed {register_count} registers, {field_count} bitfields")
            return 0

        selections = parse_selection_json(Path(args.select_json))
        targets = resolve_active_targets(selections, catalog)
        generated, metadata = generate_values(targets, catalog, args.seed)
        metadata["selected_registers"] = targets
        cfg_text = format_cfg(generated)
        write_atomic(Path(args.out), cfg_text)

        print(
            f"Parsed {register_count} registers, {field_count} bitfields; "
            f"Generated {args.out} for {len(generated)} register groups; "
            f"seed={metadata['seed']}"
        )
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

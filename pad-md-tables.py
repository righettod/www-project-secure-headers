#!/usr/bin/env python
"""Pad all markdown tables in a file so columns are vertically aligned."""

import re
import sys


def parse_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return line.split("|")


def is_separator_cell(cell):
    return bool(re.match(r"^\s*:?-+:?\s*$", cell))


def is_separator_row(row):
    return row and all(is_separator_cell(cell) for cell in row)


def pad_table(table_lines):
    rows = [parse_row(line) for line in table_lines]
    if not rows:
        return table_lines

    num_cols = max(len(r) for r in rows)
    for row in rows:
        while len(row) < num_cols:
            row.append("")

    col_widths = [0] * num_cols
    for row in rows:
        if is_separator_row(row):
            continue
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell.strip()))

    col_widths = [max(w, 3) for w in col_widths]

    result = []
    for row in rows:
        if is_separator_row(row):
            parts = []
            for i, cell in enumerate(row):
                cs = cell.strip()
                left = cs.startswith(":")
                right = cs.endswith(":") and len(cs) > 1
                w = col_widths[i]
                if left and right:
                    dashes = ":" + "-" * max(w - 2, 1) + ":"
                elif left:
                    dashes = ":" + "-" * (w - 1)
                elif right:
                    dashes = "-" * (w - 1) + ":"
                else:
                    dashes = "-" * w
                parts.append(" " + dashes + " ")
            result.append("|" + "|".join(parts) + "|")
        else:
            parts = []
            for i, cell in enumerate(row):
                content = cell.strip()
                parts.append(" " + content.ljust(col_widths[i]) + " ")
            result.append("|" + "|".join(parts) + "|")

    return result


def pad_markdown_tables(content):
    lines = content.split("\n")
    result = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            result.extend(pad_table(table_lines))
        else:
            result.append(lines[i])
            i += 1
    return "\n".join(result)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <markdown-file>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    result = pad_markdown_tables(content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Tables padded in: {path}")

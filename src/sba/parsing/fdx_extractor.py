"""Extract text from Final Draft (.fdx) screenplay files.

Final Draft XML format contains typed paragraphs:
  - Scene Heading
  - Action
  - Character
  - Dialogue
  - Parenthetical
  - Transition
  - Shot
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def extract_text_from_fdx(fdx_path: str | Path) -> str:
    """Extract screenplay text from a Final Draft .fdx file.

    Converts FDX XML into plain text with standard screenplay formatting,
    preserving scene headings, character cues, dialogue, and action.
    """
    fdx_path = Path(fdx_path)
    if not fdx_path.exists():
        raise FileNotFoundError(f"FDX file not found: {fdx_path}")

    tree = ET.parse(fdx_path)
    root = tree.getroot()

    lines: list[str] = []

    # Find all Paragraph elements in the Content section
    content = root.find(".//Content")
    if content is None:
        # Try alternative structures
        content = root

    for para in content.iter("Paragraph"):
        para_type = para.get("Type", "").strip()

        # Build the text from all Text child elements
        texts: list[str] = []
        for text_elem in para.iter("Text"):
            if text_elem.text:
                texts.append(text_elem.text)
        line = "".join(texts).strip()

        if not line:
            lines.append("")
            continue

        # Format based on paragraph type (standard screenplay layout)
        if para_type == "Scene Heading":
            lines.append("")
            lines.append(line.upper())
            lines.append("")
        elif para_type == "Action":
            lines.append(line)
            lines.append("")
        elif para_type == "Character":
            lines.append("")
            lines.append(f"                         {line.upper()}")
        elif para_type == "Parenthetical":
            lines.append(f"                    {line}")
        elif para_type == "Dialogue":
            lines.append(f"               {line}")
        elif para_type == "Transition":
            lines.append("")
            lines.append(f"                                            {line.upper()}")
            lines.append("")
        elif para_type == "Shot":
            lines.append("")
            lines.append(line.upper())
            lines.append("")
        else:
            # General / Notes / other
            lines.append(line)

    return "\n".join(lines)

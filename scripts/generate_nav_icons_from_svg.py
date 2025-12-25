"""Render navigation icons from SVG sources with active/inactive tints using PIL and svg.path."""
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageColor, ImageDraw
from svg.path import parse_path

ICON_SIZE = 128
ROOT = Path(__file__).resolve().parent.parent
SVG_DIR = ROOT / "assets" / "svg"
PNG_DIR = ROOT / "assets" / "icons"
PNG_DIR.mkdir(parents=True, exist_ok=True)

ICON_DEFINITIONS = {
    "home": "home-svgrepo-com.svg",
    "search": "search-svgrepo-com.svg",
    "settings": "settings-svgrepo-com.svg",
}

COLOR_VARIANTS = {
    "active": "#2890E6",
    "inactive": "#7F7F7F",
}

SAMPLES_PER_SEGMENT = 32


def _scale_point(point, scale):
    return point.real * scale, point.imag * scale


def _draw_path(draw, d_attr, color, stroke_width, scale):
    try:
        parsed = parse_path(d_attr)
    except Exception:
        return

    stroke_px = max(1, int(stroke_width * scale))

    for segment in parsed:
        points = []
        for step in range(SAMPLES_PER_SEGMENT + 1):
            t = step / SAMPLES_PER_SEGMENT
            pt = segment.point(t)
            point = _scale_point(pt, scale)
            points.append(point)
        draw.line(points, fill=color, width=stroke_px)


def _draw_circle(draw, cx, cy, r, color, stroke_width, scale):
    x = (cx - r) * scale
    y = (cy - r) * scale
    diameter = 2 * r * scale
    draw.ellipse([x, y, x + diameter, y + diameter], outline=color, width=max(1, int(stroke_width * scale)))


def render_icon(svg_path, color_hex):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns_scale = ICON_SIZE / float(root.attrib.get("viewBox", "0 0 24 24").split()[2])
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (*ImageColor.getrgb(color_hex), 255)

    for elem in root.iter():
        tag = elem.tag.lower()
        if tag.endswith("path") and "d" in elem.attrib:
            stroke = float(elem.attrib.get("stroke-width", "1"))
            _draw_path(draw, elem.attrib["d"], color, stroke, ns_scale)
        elif tag.endswith("circle"):
            stroke = float(elem.attrib.get("stroke-width", "1"))
            cx = float(elem.attrib.get("cx", "12"))
            cy = float(elem.attrib.get("cy", "12"))
            r = float(elem.attrib.get("r", "5"))
            _draw_circle(draw, cx, cy, r, color, stroke, ns_scale)

    return img


for icon_name, svg_name in ICON_DEFINITIONS.items():
    svg_path = SVG_DIR / svg_name
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG source not found: {svg_path}")

    for variant, color in COLOR_VARIANTS.items():
        output_path = PNG_DIR / f"{icon_name}_{variant}.png"
        image = render_icon(svg_path, color)
        image.save(output_path)
        print(f"Rendered {output_path.name} ({variant})")

print("Navigation icons generated from SVG assets.")

"""Create simple icon images for navigation buttons"""
import os
import math
from PIL import Image, ImageDraw

# Create PNG directory if it doesn't exist
png_dir = os.path.join('assets', 'icons')
os.makedirs(png_dir, exist_ok=True)

# Icon size in pixels
ICON_SIZE = 96  # 2x for retina displays

# Colors
COLOR_ACTIVE = (56, 140, 230, 255)  # Blue
COLOR_INACTIVE = (128, 128, 128, 255)  # Gray

def create_home_icon(path, color):
    """Draw a simple house icon"""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    roof_top = (ICON_SIZE // 2, ICON_SIZE // 4)
    roof_left = (ICON_SIZE // 4, ICON_SIZE // 2)
    roof_right = (ICON_SIZE * 3 // 4, ICON_SIZE // 2)
    draw.polygon([roof_top, roof_right, roof_left], fill=color)

    body_width = ICON_SIZE * 7 // 10
    body_height = ICON_SIZE * 3 // 7
    body_x = (ICON_SIZE - body_width) // 2
    body_y = ICON_SIZE // 2
    draw.rectangle([body_x, body_y, body_x + body_width, body_y + body_height], fill=color)

    door_w = body_width // 4
    door_h = body_height // 2
    door_x = ICON_SIZE // 2 - door_w // 2
    door_y = body_y + body_height - door_h
    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h], fill=(0, 0, 0, 0))
    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h], outline=color, width=2)

    img.save(path)

def create_search_icon(path, color):
    """Draw a magnifier-style search icon"""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    center = ICON_SIZE // 2
    radius = ICON_SIZE * 3 // 10
    draw.ellipse([center - radius, center - radius, center + radius, center + radius], outline=color, width=8)

    handle_length = ICON_SIZE // 3
    handle_width = 8
    handle_start = (center + radius // 2, center + radius // 2)
    handle_end = (handle_start[0] + handle_length, handle_start[1] + handle_length)
    draw.line([handle_start, handle_end], fill=color, width=handle_width)
    img.save(path)

def create_settings_icon(path, color):
    """Draw a simplified gear icon"""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    center = ICON_SIZE // 2
    outer_radius = ICON_SIZE // 3
    inner_radius = ICON_SIZE // 6
    draw.ellipse([center - outer_radius, center - outer_radius, center + outer_radius, center + outer_radius], outline=color, width=8)
    draw.ellipse([center - inner_radius, center - inner_radius, center + inner_radius, center + inner_radius], fill=color)

    cog_half = outer_radius // 4
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x = center + math.cos(rad) * (outer_radius + cog_half // 2)
        y = center + math.sin(rad) * (outer_radius + cog_half // 2)
        draw.rectangle([
            x - cog_half, y - cog_half // 2,
            x + cog_half, y + cog_half // 2
        ], fill=color)

    img.save(path)

def create_back_icon(path, color):
    """Create a left arrow/back icon"""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw an arrow pointing left
    arrow_width = 28
    arrow_height = 16
    center_x = ICON_SIZE // 2
    center_y = ICON_SIZE // 2
    points = [
        (center_x + arrow_width // 2, center_y - arrow_height // 2),
        (center_x - arrow_width // 2, center_y),
        (center_x + arrow_width // 2, center_y + arrow_height // 2),
    ]
    draw.polygon(points, fill=color)
    draw.rectangle([
        center_x - arrow_width // 2, center_y - arrow_height // 4,
        center_x + arrow_width // 2, center_y + arrow_height // 4
    ], fill=color)
    img.save(path)

# Create icons in both active and inactive colors
icon_creators = {
    'home': create_home_icon,
    'search': create_search_icon,
    'settings': create_settings_icon,
    'back': create_back_icon,
}

for name, creator_func in icon_creators.items():
    # Active version (blue)
    active_path = os.path.join(png_dir, f'{name}_active.png')
    print(f"Creating {name}_active.png...")
    creator_func(active_path, COLOR_ACTIVE)
    print(f"  ✓ Saved to {active_path}")
    
    # Inactive version (gray)
    inactive_path = os.path.join(png_dir, f'{name}_inactive.png')
    print(f"Creating {name}_inactive.png...")
    creator_func(inactive_path, COLOR_INACTIVE)
    print(f"  ✓ Saved to {inactive_path}")

print("\nIcon creation complete!")

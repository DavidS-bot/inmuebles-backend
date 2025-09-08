from PIL import Image, ImageDraw, ImageFont
import os

def create_shortcut_icon(name, color, output_path):
    size = 192
    img = Image.new('RGBA', (size, size), color + (255,))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple icon based on the shortcut type
    if "dashboard" in name.lower():
        # Dashboard icon - grid
        grid_size = 20
        margin = 40
        for i in range(3):
            for j in range(3):
                x = margin + j * (grid_size + 20)
                y = margin + i * (grid_size + 20)
                draw.rectangle([x, y, x + grid_size, y + grid_size], fill=(255, 255, 255, 255))
    
    elif "properties" in name.lower() or "propiedades" in name.lower():
        # House icon
        house_scale = 0.7
        house_width = int(80 * house_scale)
        house_height = int(50 * house_scale)
        house_x = int((size - house_width) / 2)
        house_y = int(size * 0.45)
        
        # House base
        draw.rectangle([house_x, house_y, house_x + house_width, house_y + house_height], 
                       fill=(255, 255, 255, 255))
        
        # Roof
        roof_points = [
            (house_x + house_width // 2, house_y - int(40 * house_scale)),
            (house_x - int(15 * house_scale), house_y),
            (house_x + house_width + int(15 * house_scale), house_y)
        ]
        draw.polygon(roof_points, fill=(255, 255, 255, 255))
    
    elif "finance" in name.lower() or "finanz" in name.lower():
        # Finance icon - dollar sign
        center = size // 2
        draw.ellipse([center - 50, center - 50, center + 50, center + 50], 
                     outline=(255, 255, 255, 255), width=8)
        # Simple $ symbol
        draw.line([center, center - 30, center, center + 30], fill=(255, 255, 255, 255), width=8)
        draw.arc([center - 20, center - 20, center + 20, center], 180, 360, fill=(255, 255, 255, 255), width=6)
        draw.arc([center - 20, center, center + 20, center + 20], 0, 180, fill=(255, 255, 255, 255), width=6)
    
    img.save(output_path, 'PNG')

def create_screenshot_placeholder(width, height, output_path, label):
    img = Image.new('RGB', (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple app mockup
    # Header
    draw.rectangle([0, 0, width, 60], fill=(52, 152, 219))
    
    # Title
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "Inmuebles - " + label
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) // 2, 18), text, fill=(255, 255, 255), font=font)
    
    # Content area with some placeholder elements
    card_height = 80
    card_margin = 20
    for i in range(3):
        y = 100 + i * (card_height + card_margin)
        draw.rectangle([20, y, width - 20, y + card_height], 
                       fill=(255, 255, 255), outline=(220, 220, 220))
    
    img.save(output_path, 'PNG')

# Create shortcut icons
icons_dir = "inmuebles-web/public/icons"
os.makedirs(icons_dir, exist_ok=True)

create_shortcut_icon("dashboard", (52, 152, 219), f"{icons_dir}/dashboard.png")
create_shortcut_icon("properties", (46, 204, 113), f"{icons_dir}/properties.png")
create_shortcut_icon("finance", (231, 76, 60), f"{icons_dir}/finance.png")

print("Shortcut icons created successfully!")

# Create screenshot placeholders
screenshots_dir = "inmuebles-web/public/screenshots"
os.makedirs(screenshots_dir, exist_ok=True)

create_screenshot_placeholder(390, 844, f"{screenshots_dir}/mobile-dashboard.png", "Dashboard Móvil")
create_screenshot_placeholder(1280, 720, f"{screenshots_dir}/desktop-dashboard.png", "Dashboard Escritorio")

print("Screenshot placeholders created successfully!")
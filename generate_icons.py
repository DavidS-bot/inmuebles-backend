from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    # Create a new image with a blue gradient background
    img = Image.new('RGBA', (size, size), (52, 152, 219, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple house icon
    house_scale = size / 512.0
    
    # House base
    house_width = int(152 * house_scale)
    house_height = int(100 * house_scale)
    house_x = int((size - house_width) / 2)
    house_y = int(size * 0.4)
    
    # Draw house base
    draw.rectangle([house_x, house_y, house_x + house_width, house_y + house_height], 
                   fill=(255, 255, 255, 255), outline=(236, 240, 241, 255))
    
    # Draw roof
    roof_height = int(80 * house_scale)
    roof_points = [
        (house_x + house_width // 2, house_y - roof_height),  # Top point
        (house_x - int(30 * house_scale), house_y),           # Left bottom
        (house_x + house_width + int(30 * house_scale), house_y)  # Right bottom
    ]
    draw.polygon(roof_points, fill=(255, 255, 255, 255), outline=(236, 240, 241, 255))
    
    # Draw door
    door_width = int(52 * house_scale)
    door_height = int(60 * house_scale)
    door_x = house_x + (house_width - door_width) // 2
    door_y = house_y + house_height - door_height
    draw.rectangle([door_x, door_y, door_x + door_width, door_y + door_height], 
                   fill=(52, 73, 94, 255))
    
    # Draw windows
    window_size = int(25 * house_scale)
    window_y = house_y + int(15 * house_scale)
    
    # Left window
    draw.rectangle([house_x + int(15 * house_scale), window_y, 
                   house_x + int(15 * house_scale) + window_size, window_y + window_size], 
                   fill=(52, 152, 219, 255))
    
    # Right window
    draw.rectangle([house_x + house_width - int(15 * house_scale) - window_size, window_y, 
                   house_x + house_width - int(15 * house_scale), window_y + window_size], 
                   fill=(52, 152, 219, 255))
    
    # Save the image
    img.save(output_path, 'PNG')

# Create icons directory if it doesn't exist
icons_dir = "inmuebles-web/public/icons"
os.makedirs(icons_dir, exist_ok=True)

# Generate all required icon sizes
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    output_path = f"{icons_dir}/icon-{size}x{size}.png"
    create_icon(size, output_path)
    print(f"Created icon: {output_path}")

print("All PWA icons generated successfully!")
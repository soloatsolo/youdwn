from PIL import Image, ImageDraw

# Create a new image with a red background
size = (64, 64)
icon = Image.new('RGB', size, 'red')

# Create a drawing object
draw = ImageDraw.Draw(icon)

# Draw a white play triangle
center_x = size[0] // 2
center_y = size[1] // 2
triangle_size = 24
points = [
    (center_x - triangle_size//2, center_y - triangle_size//2),
    (center_x - triangle_size//2, center_y + triangle_size//2),
    (center_x + triangle_size//2, center_y)
]
draw.polygon(points, fill='white')

# Save the icon
icon.save('icon.png')
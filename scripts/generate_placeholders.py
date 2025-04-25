import os
from PIL import Image, ImageDraw, ImageFont
import random


def generate_placeholder_image(name, output_path, width=800, height=400):
    """Generate a placeholder image for a parking location."""
    # Create a new image with a random background color
    img = Image.new(
        "RGB",
        (width, height),
        color=(
            random.randint(200, 255),
            random.randint(200, 255),
            random.randint(200, 255),
        ),
    )

    # Get a drawing context
    draw = ImageDraw.Draw(img)

    # Draw a colored rectangle in the center
    rect_width = width * 0.8
    rect_height = height * 0.6
    rect_x = (width - rect_width) / 2
    rect_y = (height - rect_height) / 2

    # Draw the rectangle with a random color
    draw.rectangle(
        [(rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height)],
        fill=(
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200),
        ),
    )

    # Add some "parking" elements
    # Parking lines
    line_spacing = 40
    line_width = 5
    line_y = rect_y + 20
    while line_y < rect_y + rect_height - 20:
        draw.rectangle(
            [(rect_x + 20, line_y), (rect_x + rect_width - 20, line_y + line_width)],
            fill=(255, 255, 255),
        )
        line_y += line_spacing

    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Draw the parking name
    text_width = draw.textlength(name, font=font)
    text_x = (width - text_width) / 2
    text_y = height * 0.1
    draw.text((text_x, text_y), name, fill=(0, 0, 0), font=font)

    # Add "PARKING" text
    parking_text = "PARKING"
    parking_width = draw.textlength(parking_text, font=font)
    parking_x = (width - parking_width) / 2
    parking_y = height * 0.75
    draw.text((parking_x, parking_y), parking_text, fill=(0, 0, 0), font=font)

    # Save the image
    img.save(output_path)
    print(f"Generated image for {name} at {output_path}")


def main():
    # Make sure the output directory exists
    output_dir = "app/static/images/parking"
    os.makedirs(output_dir, exist_ok=True)

    # List of parking locations
    locations = [
        "alpha_one",
        "himalaya_mall",
        "palladium_mall",
        "central_mall",
        "riverfront",
        "iscon_mall",
    ]

    # Generate an image for each location
    for location in locations:
        # Format the location name for display
        display_name = location.replace("_", " ").title() + " Parking"

        # Generate the image
        output_path = os.path.join(output_dir, f"{location}.jpg")
        generate_placeholder_image(display_name, output_path)


if __name__ == "__main__":
    main()

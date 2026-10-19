import os
from PIL import Image, ImageDraw

def create_tactical_icon():
    os.makedirs("assets", exist_ok=True)
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (10, 10, 10, 255))
        draw = ImageDraw.Draw(img)

        # Draw outer hazard border
        border_width = max(1, size // 32)
        draw.rectangle(
            [(0, 0), (size - 1, size - 1)],
            outline=(204, 255, 0, 255),  # #CCFF00 Acid Lime
            width=border_width
        )

        # Draw brutalist folder geometry
        pad = size // 5
        fw = size - (pad * 2)
        fh = int(fw * 0.7)
        top = size // 3

        # Folder tab
        tab_w = int(fw * 0.4)
        tab_h = max(2, size // 12)
        draw.rectangle(
            [(pad, top - tab_h), (pad + tab_w, top)],
            fill=(255, 68, 0, 255)  # #FF4400 Hazard Orange Tab
        )

        # Folder body
        draw.rectangle(
            [(pad, top), (pad + fw, top + fh)],
            fill=(204, 255, 0, 255),  # Acid Lime
            outline=(10, 10, 10, 255),
            width=max(1, size // 32)
        )

        # Inner diagonal slash (Streetwear slash)
        slash_w = max(1, size // 16)
        draw.line(
            [(pad + 2, top + fh - 2), (pad + fw - 2, top + 2)],
            fill=(10, 10, 10, 255),
            width=slash_w
        )

        images.append(img)

    # Save PNG & ICO
    images[-1].save("assets/icon.png", format="PNG")
    images[-1].save("assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
    print("Tactical icon generated at assets/icon.ico and assets/icon.png")

if __name__ == "__main__":
    create_tactical_icon()

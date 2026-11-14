"""Draw the BloomDepth logo on a 32-pixel grid."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def draw_icon():
    image = Image.new("RGB", (32, 32), "#20352e")
    draw = ImageDraw.Draw(image)
    draw.rectangle((1, 1, 30, 30), fill="#375244")

    draw.polygon(
        [(14, 27), (14, 22), (9, 22), (5, 19), (4, 16), (9, 16),
         (13, 18), (16, 21), (18, 18), (22, 17), (27, 17), (26, 21),
         (23, 24), (18, 24), (18, 28), (14, 28)],
        fill="#21352d",
    )
    draw.polygon([(6, 17), (10, 17), (15, 21), (10, 21), (7, 19)], fill="#78a755")
    draw.polygon([(17, 22), (21, 18), (25, 18), (24, 21), (21, 23), (17, 23)], fill="#619451")
    draw.rectangle((15, 16, 16, 26), fill="#84ae5c")

    draw.polygon(
        [(12, 4), (18, 4), (18, 6), (22, 6), (22, 9), (24, 9),
         (24, 14), (22, 14), (22, 17), (18, 17), (18, 19), (12, 19),
         (12, 17), (8, 17), (8, 14), (6, 14), (6, 9), (8, 9),
         (8, 6), (12, 6)],
        fill="#542c44",
    )
    draw.rectangle((13, 5, 17, 17), fill="#df769a")
    draw.rectangle((9, 7, 21, 15), fill="#de608e")
    draw.rectangle((7, 10, 22, 13), fill="#ed85a8")
    draw.rectangle((10, 8, 14, 10), fill="#ffb5c8")
    draw.rectangle((12, 14, 17, 16), fill="#f18fac")
    draw.rectangle((13, 9, 17, 13), fill="#c8883c")
    draw.rectangle((13, 9, 16, 12), fill="#ffda78")
    draw.point((14, 10), fill="#fff1b4")
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curseforge", type=Path, help="Also write a 512px PNG")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    image = draw_icon()
    image.resize((128, 128), Image.Resampling.NEAREST).save(
        root / "src/main/resources/assets/bloomdepth/icon.png"
    )
    if args.curseforge:
        image.resize((512, 512), Image.Resampling.NEAREST).save(args.curseforge)


if __name__ == "__main__":
    main()

import os 

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys
import pygame
import json

def load_json(file):
    with open(file, "r", encoding="utf-8") as fp:
        return json.load(fp)
    return {}

def image_to_asm(input_image_path, width, height,config):
    size = 4
    img = pygame.image.load(input_image_path)

    tiles_x = img.get_width() // size
    tiles_y = img.get_height() // size

    values = []
    ff_line = ",".join(["$FF"] * width)
    dels = 0
    xxw = tiles_x//width
    yyh = tiles_y//height
    for xx in range(xxw):
        for yy in range(yyh):
            vy = []
            for ty in range(height):
                vx = []
                for tx in range(width):
                    x = (xx*width+tx) * size
                    y = (yy*height+ty) * size
                    idx0 = img.get_at_mapped((x + 0, y + 0)) & 0x0F
                    idx1 = img.get_at_mapped((x + 1, y + 0)) & 0x0F
                    vx.append(f"${((idx0 << 4) | idx1):02X}")
                vy.append(",".join(vx))
            if all(v == ff_line for v in vy): dels+=1; continue
            values.append(vy)
    if dels == 0:
        print(f"; all {len(values)} = {xxw*yyh} = {xxw}x{yyh}")
    else:
        print(f"; all {len(values)} = {xxw*yyh} - {dels} = {xxw}x{yyh} - {dels}")

    first_value=0
    if len(config["data"].values()) != 0:
        first_value = next(iter(config["data"].values()))
        print(f"; first_value {first_value}")

    for i,vy in enumerate(values):
        keys = [k for k, v in config["data"].items() if v == i+first_value]
        if len(keys) > 0:
            for k in keys:
                print(f"{k}: ; {i+first_value}")
        else:
            print(f"; {i+first_value}")
        for v in vy:
            print("    db " + v)
    print(f"; all {len(values)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mkimg2asm.py <input_image.png> <input.json>")
        sys.exit(1)
    config = load_json(sys.argv[2]) if len(sys.argv) >= 3 else {}
    width = 11
    height = 10

    image_to_asm(sys.argv[1], width, height,config)

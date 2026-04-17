from PIL import ImageDraw
from config import MAP_WIDTH, MAP_HEIGHT

TILE_SIZE = 12

def draw_frontline_marker(draw: ImageDraw.ImageDraw, coord: str, color: tuple = (255, 50, 50)):
    col = ord(coord[0].upper()) - 65
    row = int(coord[1:]) - 1
    x = col * TILE_SIZE
    y = row * TILE_SIZE
    cx = x + TILE_SIZE // 2
    cy = y + TILE_SIZE // 2
    r = TILE_SIZE // 4
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

def draw_army_marker(draw: ImageDraw.ImageDraw, coord: str, color: tuple = (255, 255, 255)):
    col = ord(coord[0].upper()) - 65
    row = int(coord[1:]) - 1
    x = col * TILE_SIZE
    y = row * TILE_SIZE
    draw.rectangle([x + 2, y + 2, x + TILE_SIZE - 3, y + TILE_SIZE - 3], outline=color, width=1)

def draw_grid(draw: ImageDraw.ImageDraw):
    from renderer.tile_sprites import BORDER_COLOR
    for col in range(MAP_WIDTH):
        x = col * TILE_SIZE
        draw.line([(x, 0), (x, MAP_HEIGHT * TILE_SIZE)], fill=BORDER_COLOR, width=1)
    for row in range(MAP_HEIGHT):
        y = row * TILE_SIZE
        draw.line([(0, y), (MAP_WIDTH * TILE_SIZE, y)], fill=BORDER_COLOR, width=1)

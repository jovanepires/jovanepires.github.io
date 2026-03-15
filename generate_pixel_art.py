from PIL import Image, ImageDraw

# Logical canvas size
W, H = 150, 79

# Colors
SKY = (13, 17, 23)          # #0D1117 dark navy
GROUND = (92, 138, 60)      # #5C8A3C bright ground
GROUND_DARK = (60, 90, 35)  # darker ground line
PIPE_GREEN = (58, 140, 63)  # #3A8C3F
PIPE_DARK = (45, 107, 49)   # #2D6B31 shadow
PIPE_LIGHT = (80, 170, 85)  # highlight
WHITE = (255, 255, 255)
STAR = (200, 210, 220)
CHAR_BLUE = (50, 100, 200)
CHAR_SKIN = (230, 190, 140)
CHAR_HAT = (40, 160, 80)
ARROW_COLOR = (255, 220, 50)  # yellow arrow/speed lines

img = Image.new("RGB", (W, H), SKY)
draw = ImageDraw.Draw(img)

# --- STARS ---
stars = [
    (5, 3), (12, 7), (22, 2), (35, 5), (48, 1), (60, 6), (72, 3),
    (83, 8), (95, 2), (108, 5), (120, 1), (130, 4), (143, 7),
    (15, 12), (55, 10), (80, 14), (110, 11), (140, 9),
    (28, 18), (65, 15), (100, 17), (135, 13),
    (8, 22), (45, 20), (90, 25), (125, 19),
    (3, 30), (70, 28), (115, 32),
    (20, 35), (50, 33), (88, 38),
]
for sx, sy in stars:
    draw.point((sx, sy), fill=STAR)

# Ground strip: rows 70-78
for y in range(70, 79):
    for x in range(W):
        if y == 70:
            draw.point((x, y), fill=GROUND_DARK)
        else:
            draw.point((x, y), fill=GROUND)

# Helper: draw a pipe
def draw_pipe(draw, x_center, pipe_top, pipe_bottom, pipe_w=16, cap_w=20):
    """
    x_center: center x of the pipe
    pipe_top: top y of the pipe body (below cap)
    pipe_bottom: bottom y (ground line = 70)
    pipe_w: width of pipe body
    cap_w: width of cap
    """
    cap_h = 4
    cap_top = pipe_top - cap_h

    # --- Pipe body ---
    bx0 = x_center - pipe_w // 2
    bx1 = x_center + pipe_w // 2 - 1
    for y in range(pipe_top, pipe_bottom + 1):
        for x in range(bx0, bx1 + 1):
            if x == bx0 or x == bx0 + 1:
                draw.point((x, y), fill=PIPE_LIGHT)
            elif x == bx1 or x == bx1 - 1:
                draw.point((x, y), fill=PIPE_DARK)
            else:
                draw.point((x, y), fill=PIPE_GREEN)

    # --- Pipe cap ---
    cx0 = x_center - cap_w // 2
    cx1 = x_center + cap_w // 2 - 1
    for y in range(cap_top, pipe_top):
        for x in range(cx0, cx1 + 1):
            if x == cx0 or x == cx0 + 1:
                draw.point((x, y), fill=PIPE_LIGHT)
            elif x == cx1 or x == cx1 - 1:
                draw.point((x, y), fill=PIPE_DARK)
            else:
                draw.point((x, y), fill=PIPE_GREEN)

    # Top edge of cap (bright line)
    for x in range(cx0, cx1 + 1):
        draw.point((x, cap_top), fill=PIPE_LIGHT)

# Left pipe: tall, x_center=48, top=8 (very tall)
LEFT_CENTER = 48
LEFT_TOP = 8
draw_pipe(draw, LEFT_CENTER, pipe_top=LEFT_TOP, pipe_bottom=69)

# Right pipe: short, x_center=105
RIGHT_CENTER = 105
RIGHT_TOP = 55
draw_pipe(draw, RIGHT_CENTER, pipe_top=RIGHT_TOP, pipe_bottom=69)

# --- PIXEL TEXT (hand-drawn bitmaps, 4x5 grid per char) ---
FONT = {
    # digits
    '0': [(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(3,3),(1,4),(2,4)],
    '1': [(1,0),(0,1),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
    '2': [(0,0),(1,0),(2,0),(3,1),(2,2),(1,2),(0,3),(0,4),(1,4),(2,4),(3,4)],
    '5': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(3,3),(0,4),(1,4),(2,4)],
    # uppercase letters
    'M': [(0,0),(3,0),(0,1),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(3,3),(0,4),(3,4)],
    'I': [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
    'N': [(0,0),(0,1),(0,2),(0,3),(0,4),(1,1),(2,2),(3,0),(3,1),(3,2),(3,3),(3,4)],
    'S': [(1,0),(2,0),(0,1),(1,2),(2,2),(3,3),(1,4),(2,4)],
    # symbols
    '~': [(0,1),(1,0),(2,1),(3,2),(4,1)],
    ' ': [],
}

def draw_text(draw, text, x, y, color=WHITE, char_w=4, char_h=5, gap=1):
    cx = x
    for ch in text:
        pixels = FONT.get(ch, [])
        for px, py in pixels:
            draw.point((cx + px, y + py), fill=color)
        cx += char_w + gap

def text_width(text, char_w=4, gap=1):
    return len(text) * (char_w + gap) - gap

# Label above left pipe: "15 MIN"
label_left = "15 MIN"
lw = text_width(label_left)
draw_text(draw, label_left, LEFT_CENTER - lw // 2, LEFT_TOP - 8, color=WHITE)

# Label above right pipe: "~1S"
label_right = "~1S"
rw = text_width(label_right)
draw_text(draw, label_right, RIGHT_CENTER - rw // 2, RIGHT_TOP - 8, color=WHITE)

# --- SPEED ARROW / LINES from left pipe area toward right pipe ---
# Draw a horizontal dashed arrow at mid-height between the two pipes
arrow_y = 40
# Dashes
for x in range(62, 87, 4):
    draw.point((x, arrow_y), fill=ARROW_COLOR)
    draw.point((x + 1, arrow_y), fill=ARROW_COLOR)
# Arrowhead pointing right
draw.point((87, arrow_y), fill=ARROW_COLOR)
draw.point((88, arrow_y), fill=ARROW_COLOR)
draw.point((88, arrow_y - 1), fill=ARROW_COLOR)
draw.point((88, arrow_y + 1), fill=ARROW_COLOR)
draw.point((89, arrow_y - 2), fill=ARROW_COLOR)
draw.point((89, arrow_y + 2), fill=ARROW_COLOR)

# Speed lines above arrow (suggest motion)
for i, sx in enumerate(range(64, 84, 6)):
    draw.point((sx, arrow_y - 2), fill=ARROW_COLOR)
    draw.point((sx + 1, arrow_y - 2), fill=ARROW_COLOR)

# --- PIXEL CHARACTER near right pipe (simple humanoid, blue outfit, green hat) ---
# Standing to the left of the right pipe, at ground level
cx = RIGHT_CENTER - 14  # character center x ~= 91
ground_y = 69  # ground top

# Feet (2 px wide, 1 px tall)
draw.point((cx - 1, ground_y - 1), fill=CHAR_BLUE)
draw.point((cx, ground_y - 1), fill=CHAR_BLUE)
draw.point((cx + 1, ground_y - 1), fill=CHAR_BLUE)

# Legs
draw.point((cx - 1, ground_y - 2), fill=CHAR_BLUE)
draw.point((cx + 1, ground_y - 2), fill=CHAR_BLUE)

# Body (blue)
for by in range(ground_y - 5, ground_y - 2):
    draw.point((cx - 1, by), fill=CHAR_BLUE)
    draw.point((cx, by), fill=CHAR_BLUE)
    draw.point((cx + 1, by), fill=CHAR_BLUE)

# Arms stretched out (happy pose) - pointing right toward pipe
draw.point((cx - 2, ground_y - 4), fill=CHAR_BLUE)
draw.point((cx + 2, ground_y - 4), fill=CHAR_BLUE)
draw.point((cx + 3, ground_y - 5), fill=CHAR_BLUE)  # arm raised up right

# Head (skin)
for hy in range(ground_y - 8, ground_y - 5):
    draw.point((cx - 1, hy), fill=CHAR_SKIN)
    draw.point((cx, hy), fill=CHAR_SKIN)
    draw.point((cx + 1, hy), fill=CHAR_SKIN)

# Eyes (white dots)
draw.point((cx - 1, ground_y - 7), fill=WHITE)
draw.point((cx + 1, ground_y - 7), fill=WHITE)

# Smile (pixel smile: 3 dots at bottom of face row)
draw.point((cx - 1, ground_y - 6), fill=(80, 40, 20))
draw.point((cx + 1, ground_y - 6), fill=(80, 40, 20))

# Hat (green, 1px brim + 2px crown)
# Brim
for hx in range(cx - 2, cx + 3):
    draw.point((hx, ground_y - 9), fill=CHAR_HAT)
# Crown
for hy in range(ground_y - 12, ground_y - 9):
    draw.point((cx - 1, hy), fill=CHAR_HAT)
    draw.point((cx, hy), fill=CHAR_HAT)
    draw.point((cx + 1, hy), fill=CHAR_HAT)

# --- Scale up to 1200x630 with NEAREST ---
out = img.resize((1200, 630), Image.NEAREST)
out.save(
    "/home/user/jovanepires.github.io/static/images/spark-pytest-terminal.jpg",
    "JPEG",
    quality=95
)
print("Done! Image saved.")

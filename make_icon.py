import colorsys
import math
from PIL import Image, ImageDraw

SIZE = 512
SS = 4
img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

cx, cy = SIZE * SS / 2, SIZE * SS / 2
R = SIZE * SS * 0.187
stroke = SIZE * SS * 0.120
offset = R * 1.12

# sanity check: the whole shape (both loops + stroke) must fit inside the
# canvas with a margin, otherwise it gets clipped when scaled down to
# small icon sizes (16/32/48px) and taskbar/title-bar display.
half_width = offset + R + stroke / 2
half_height = R + stroke / 2
assert half_width <= SIZE * SS * 0.48, half_width
assert half_height <= SIZE * SS * 0.48, half_height

HUE_ORANGE = 0.07
HUE_GREEN = 0.36
HUE_PURPLE = 0.80
SAT, VAL = 0.85, 0.98

N = 3000


def hsv(hue):
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, SAT, VAL)
    return int(r * 255), int(g * 255), int(b * 255), 255


for i in range(N):
    s = i / N
    angle = math.pi + s * 2 * math.pi
    x = cx + offset + R * math.cos(angle)
    y = cy + R * math.sin(angle)
    hue = HUE_GREEN + (1 - 2 * abs(s - 0.5)) * (HUE_PURPLE - HUE_GREEN)
    draw.ellipse((x - stroke / 2, y - stroke / 2, x + stroke / 2, y + stroke / 2),
                 fill=hsv(hue))

for i in range(N):
    s = i / N
    angle = s * 2 * math.pi
    x = cx - offset + R * math.cos(angle)
    y = cy + R * math.sin(angle)
    hue = HUE_ORANGE + 2 * abs(s - 0.5) * (HUE_GREEN - HUE_ORANGE)
    draw.ellipse((x - stroke / 2, y - stroke / 2, x + stroke / 2, y + stroke / 2),
                 fill=hsv(hue))

img = img.resize((SIZE, SIZE), Image.LANCZOS)
img.save("infinite_logo.png")

sizes = [16, 24, 32, 48, 64, 128, 256]
img.save("infinite_logo.ico", sizes=[(s, s) for s in sizes])
print("done, half_width_ratio=", half_width / (SIZE * SS), "half_height_ratio=", half_height / (SIZE * SS))

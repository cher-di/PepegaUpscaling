from PIL import Image


__all__ = [
    'bright',
    'negative',
    'white_black',
    'gray_scale',
    'sepia',
    'contrast',
]


def bright(source_name, result_name, brightness):
    source = Image.open(source_name)
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            red = int(r * brightness)
            red = min(255, max(0, red))
            green = int(g * brightness)
            green = min(255, max(0, green))
            blue = int(b * brightness)
            blue = min(255, max(0, blue))
            result.putpixel((x, y), (red, green, blue))
    result.save(result_name, "PNG")


def negative(source_name, result_name):
    source = Image.open(source_name)
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            result.putpixel((x, y), (255 - r, 255 - g, 255 - b))
    result.save(result_name, "PNG")


def white_black(source_name, result_name, brightness):
    source = Image.open(source_name)
    result = Image.new('RGB', source.size)
    separator = 255 / brightness / 2 * 3
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            total = r + g + b
            if total > separator:
                result.putpixel((x, y), (255, 255, 255))
            else:
                result.putpixel((x, y), (0, 0, 0))
    result.save(result_name, "PNG")


def gray_scale(source_name, result_name):
    source = Image.open(source_name)
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            gray = int(r * 0.2126 + g * 0.7152 + b * 0.0722)
            result.putpixel((x, y), (gray, gray, gray))
    result.save(result_name, "PNG")


def sepia(source_name, result_name):
    source = Image.open(source_name)
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            red = int(r * 0.393 + g * 0.769 + b * 0.189)
            green = int(r * 0.349 + g * 0.686 + b * 0.168)
            blue = int(r * 0.272 + g * 0.534 + b * 0.131)
            result.putpixel((x, y), (red, green, blue))
    result.save(result_name, "PNG")


def contrast(source_name, result_name, coefficient):
    source = Image.open(source_name)
    result = Image.new('RGB', source.size)

    avg = 0
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            avg += r * 0.299 + g * 0.587 + b * 0.114
    avg /= source.size[0] * source.size[1]

    palette = []
    for i in range(256):
        temp = int(avg + coefficient * (i - avg))
        if temp < 0:
            temp = 0
        elif temp > 255:
            temp = 255
        palette.append(temp)

    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))[:3]
            result.putpixel((x, y), (palette[r], palette[g], palette[b]))

    result.save(result_name, "PNG")

# Tests
# contrast("./output/test.png", "./output/contrast.png", 2)
# sepia("./output/test.png", "./output/sepia.png")
# bright("./output/test.png", "./output/brighter.png", 1.5)
# bright("./output/test.png", "./output/darker.png", 0.5)
# negative("./output/test.png", "./output/negative.png")
# white_black("./output/test.png", "./output/white_black_darker.png", 0.5)
# white_black("./output/test.png", "./output/white_black_brighter.png", 1.5)
# gray_scale("./output/test.png", "./output/gray_scale.png")

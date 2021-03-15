import enum


class Filters(enum.Enum):
    BRIGHT = 'bright'
    NEGATIVE = 'negative'
    WHITE_BLACK = 'white_black'
    GRAY_SCALE = 'gray_scale'
    SEPIA = 'sepia'
    CONTRAST = 'contrast'

    UPSCALE_X2 = 'upscale_x2'
    UPSCALE_X4 = 'upscale_x4'

    def __str__(self):
        return self.value

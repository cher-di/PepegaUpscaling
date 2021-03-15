import pytest
import hashlib

from pepegaupscaling.filters import *
from test import read_sample


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('source', 'image_filter', 'expected'),
    [
        pytest.param('source.png', Contrast(2.0), 'contrast.png', id='contrast'),
        pytest.param('source.png', Sepia(), 'sepia.png', id='sepia'),
        pytest.param('source.png', Bright(1.5), 'brighter.png', id='brighter'),
        pytest.param('source.png', Bright(0.5), 'darker.png', id='darker'),
        pytest.param('source.png', Negative(), 'negative.png', id='negative'),
        pytest.param('source.png', WhiteBlack(0.5), 'white_black_darker.png', id='white_black_darker'),
        pytest.param('source.png', WhiteBlack(1.5), 'white_black_brighter.png', id='white_black_brighter'),
        pytest.param('source.png', GrayScale(), 'gray_scale.png', id='gray_scale'),
        pytest.param('hedgehog.png', UpscaleX2(), 'hedgehog_x2.png', id='upscale_x2_png'),
        pytest.param('hedgehog.png', UpscaleX4(), 'hedgehog_x4.png', id='upscale_x4_png'),
        pytest.param('brotherhood.jpg', UpscaleX2(), 'brotherhood_x2.png', id='upscale_x2_jpg'),
        pytest.param('brotherhood.jpg', UpscaleX4(), 'brotherhood_x4.png', id='upscale_x4_jpg'),
    ]
)
async def test_filter(source, image_filter, expected):
    source_image = read_sample(source)
    result_image = await image_filter.apply(source_image)
    expected_image = read_sample(expected)
    assert hashlib.md5(result_image).hexdigest() == hashlib.md5(expected_image).hexdigest()

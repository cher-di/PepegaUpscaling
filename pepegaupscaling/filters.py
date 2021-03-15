import abc
import tempfile
import os
import subprocess
import sys
import imghdr
import io
import asyncio

from .ESRGAN.filters import *

__all__ = [
    'Filter',

    'Bright',
    'Negative',
    'WhiteBlack',
    'GrayScale',
    'Sepia',
    'Contrast',

    'UpscaleX2',
    'UpscaleX4',
]

SOURCE_ROOT = os.path.dirname(__file__)
ESRGAN_ROOT = os.path.join(SOURCE_ROOT, 'ESRGAN')
UPSCALE = os.path.join(ESRGAN_ROOT, 'upscale.py')


class TempFile:
    def __init__(self, filepath: str or None = None):
        self._filepath = filepath or tempfile.mktemp()

    def __enter__(self):
        open(self._filepath, 'wb').close()
        return self._filepath

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self._filepath):
            os.remove(self._filepath)


class Filter(abc.ABC):

    @abc.abstractmethod
    async def apply(self, image: bytes) -> bytes:
        pass


class Bright(Filter):
    def __init__(self, brightness: float):
        self._brightness = brightness

    async def apply(self, image: bytes) -> bytes:
        with TempFile() as source_file, TempFile() as result_file:
            with open(source_file, 'wb') as file:
                file.write(image)

            bright(source_file, result_file, self._brightness)

            with open(result_file, 'rb') as file:
                return file.read()


class Negative(Filter):
    async def apply(self, image: bytes) -> bytes:
        with TempFile() as source_file, TempFile() as result_file:
            with open(source_file, 'wb') as file:
                file.write(image)

            negative(source_file, result_file)

            with open(result_file, 'rb') as file:
                return file.read()


class WhiteBlack(Filter):
    def __init__(self, brightness: float):
        self._brightness = brightness

    async def apply(self, image: bytes) -> bytes:
        with TempFile() as source_file, TempFile() as result_file:
            with open(source_file, 'wb') as file:
                file.write(image)

            white_black(source_file, result_file, self._brightness)

            with open(result_file, 'rb') as file:
                return file.read()


class GrayScale(Filter):
    async def apply(self, image: bytes) -> bytes:
        with TempFile() as source_file, TempFile() as result_file:
            with open(source_file, 'wb') as file:
                file.write(image)

            gray_scale(source_file, result_file)

            with open(result_file, 'rb') as file:
                return file.read()


class Sepia(Filter):
    async def apply(self, image: bytes) -> bytes:
        with TempFile() as source_file, TempFile() as result_file:
            with open(source_file, 'wb') as file:
                file.write(image)

            sepia(source_file, result_file)

            with open(result_file, 'rb') as file:
                return file.read()


class Contrast(Filter):
    def __init__(self, coefficient: float):
        self._coefficient = coefficient

    async def apply(self, image: bytes) -> bytes:
        with TempFile() as source_file, TempFile() as result_file:
            with open(source_file, 'wb') as file:
                file.write(image)

            contrast(source_file, result_file, self._coefficient)

            with open(result_file, 'rb') as file:
                return file.read()


class Upscale(Filter, abc.ABC):
    @abc.abstractmethod
    def model(self) -> str:
        pass

    async def apply(self, image: bytes) -> bytes:
        with tempfile.TemporaryDirectory() as source_dir, \
                tempfile.TemporaryDirectory() as result_dir:

            image_type = imghdr.what(io.BytesIO(image))
            if image_type == 'png':
                source_filename = 'pepega_upscale.png'
            elif image_type == 'jpeg':
                source_filename = 'pepega_upscale.jpg'

            source_filepath = os.path.join(source_dir, source_filename)

            with open(source_filepath, 'wb') as file:
                file.write(image)

            process = await asyncio.create_subprocess_exec(sys.executable, UPSCALE,
                                                           '--input', source_dir,
                                                           '--output', result_dir,
                                                           self.model(),
                                                           stdout=asyncio.subprocess.DEVNULL,
                                                           stderr=asyncio.subprocess.DEVNULL)
            await process.wait()

            result_filename = os.listdir(result_dir)[0]
            result_filepath = os.path.join(result_dir, result_filename)

            with open(result_filepath, 'rb') as file:
                return file.read()


class UpscaleX2(Upscale):
    def model(self) -> str:
        return os.path.join(ESRGAN_ROOT, 'models', '2x.pth')


class UpscaleX4(Upscale):
    def model(self) -> str:
        return os.path.join(ESRGAN_ROOT, 'models', '4x.pth')

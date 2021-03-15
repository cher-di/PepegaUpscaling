import imghdr
import io
import asyncio
import websockets
import re
import json
import jsonschema
import datetime

from urllib.parse import urlparse

from . import Filters
from .filters import *
from .schemas import FILTERS_DATA
from .database import Database


class StatusCodes:
    OK = 200
    INVALID_JSON = 410
    INVALID_JSON_FORMAT = 411
    INVALID_IMAGE_FORMAT = 420
    INVALID_IMAGE = 421


class Server(Exception):
    pass


class InvalidImageFormat(Server):
    pass


class FileIsNotAnImage(Server):
    pass


class Server:
    def __init__(self, host: str, port: int, database: Database):
        self._host = host
        self._port = port
        self._database = database

    def run(self):
        socket = websockets.serve(self._serve,
                                  self._host,
                                  self._port,
                                  max_queue=None,
                                  max_size=None)

        asyncio.get_event_loop().run_until_complete(socket)
        asyncio.get_event_loop().run_forever()

    async def _serve(self, websocket: websockets.WebSocketServerProtocol, path: str):
        path = urlparse(path).path

        if re.fullmatch('\/api\/v1\/filters(\/|)', path):
            data = json.dumps(list(map(str, Filters)))
            await websocket.send(data)
        if re.fullmatch('\/api\/v1\/filters\/stat(\/|)', path):
            data = self._database.get_last_30_days_stat(datetime.datetime.now())
            await websocket.send(json.dumps(data))
            return
        elif re.fullmatch('\/api\/v1\/filters\/apply(\/|)', path):
            data = await websocket.recv()

            try:
                filters_data = json.loads(data)
            except json.JSONDecodeError as e:
                await websocket.send(json.dumps({
                    "status": StatusCodes.INVALID_JSON,
                    "error": e.msg,
                }))
                return

            try:
                jsonschema.validate(filters_data, FILTERS_DATA, jsonschema.Draft7Validator)
            except jsonschema.ValidationError as e:
                await websocket.send(json.dumps({
                    "status": StatusCodes.INVALID_JSON_FORMAT,
                    "error": e.message,
                }))
                return

            await websocket.send(json.dumps({
                "status": StatusCodes.OK,
            }))

            image = await websocket.recv()

            try:
                self.check_image(image)
            except InvalidImageFormat:
                await websocket.send(json.dumps({
                    "status": StatusCodes.INVALID_IMAGE_FORMAT,
                    "error": "Invalid image format",
                }))
                return
            except FileIsNotAnImage:
                await websocket.send(json.dumps({
                    "status": StatusCodes.INVALID_IMAGE,
                    "error": "File is not an image",
                }))
                return

            await websocket.send(json.dumps({
                "status": 200,
            }))

            remote_ip = websocket.remote_address[0]
            self._database.insert_request(datetime.datetime.now(), remote_ip,
                                          [filter_data["name"] for filter_data in filters_data])

            image_filters = [self._make_filter(filter_data) for filter_data in filters_data]

            result_image = image

            for _filter in image_filters:
                result_image = await _filter.apply(result_image)

            await websocket.send(result_image)

    @staticmethod
    def _make_filter(filter_data: dict):
        if filter_data['name'] == Filters.CONTRAST.value:
            return Contrast(filter_data['params']['coefficient'])
        elif filter_data['name'] == Filters.SEPIA.value:
            return Sepia()
        elif filter_data['name'] == Filters.BRIGHT.value:
            return Bright(filter_data['params']['coefficient'])
        elif filter_data['name'] == Filters.NEGATIVE.value:
            return Negative()
        elif filter_data['name'] == Filters.WHITE_BLACK.value:
            return WhiteBlack(filter_data['params']['coefficient'])
        elif filter_data['name'] == Filters.GRAY_SCALE.value:
            return GrayScale()
        elif filter_data['name'] == Filters.UPSCALE_X2.value:
            return UpscaleX2()
        elif filter_data['name'] == Filters.UPSCALE_X4.value:
            return UpscaleX4()

    @staticmethod
    def check_image(image: bytes):
        image_type = imghdr.what(io.BytesIO(image))
        if image_type is None:
            raise FileIsNotAnImage()
        elif image_type not in ('jpeg', 'png'):
            raise InvalidImageFormat()

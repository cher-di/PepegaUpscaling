import pytest
import pytest_asyncio
import websockets
import threading
import json
import hashlib
import asyncio
import time
import logging
import tempfile
import os
import datetime

logging.basicConfig(level=logging.DEBUG)

from pepegaupscaling.server import Filters, Server, StatusCodes
from pepegaupscaling.database import Database, create_database
from test import read_sample


def run_server(host: str, port: int, db_file: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    create_database(db_file)
    database = Database(db_file)
    server = Server(host, port, database)
    server.run()


@pytest.fixture(scope='module')
def server():
    db_file = tempfile.mktemp()
    host = 'localhost'
    port = 8888
    threading.Thread(target=run_server,
                     args=(host, port, db_file),
                     daemon=True).start()
    time.sleep(1.0)
    yield host, port
    os.remove(db_file)


@pytest.mark.asyncio
async def test_valid_image(server):
    image_filters = [
        {
            "name": Filters.SEPIA.value,
            "params": {}
        },
        {
            "name": Filters.BRIGHT.value,
            "params": {
                "coefficient": 1.5
            }
        },
        {
            "name": Filters.UPSCALE_X2.value,
            "params": {}
        }
    ]
    source_image = read_sample('server_source.png')
    expected_image = read_sample('server_result.png')
    host, port = server
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/apply') as websocket:
        await websocket.send(json.dumps(image_filters))
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.OK

        await websocket.send(source_image)
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.OK

        result_image = await websocket.recv()

    assert hashlib.md5(result_image).hexdigest() == hashlib.md5(expected_image).hexdigest()


@pytest.mark.asyncio
async def test_invalid_image(server):
    image_filters = [
        {
            "name": "negative",
            "params": {}
        }
    ]
    source_image = b'not_an_image'
    host, port = server
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/apply') as websocket:
        await websocket.send(json.dumps(image_filters))
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.OK

        await websocket.send(source_image)
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.INVALID_IMAGE
        await websocket.wait_closed()
        assert websocket.closed


@pytest.mark.asyncio
async def test_invalid_image_format(server):
    image_filters = [
        {
            "name": "negative",
            "params": {}
        }
    ]
    source_image = read_sample('omelette.gif')
    host, port = server
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/apply') as websocket:
        await websocket.send(json.dumps(image_filters))
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.OK

        await websocket.send(source_image)
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.INVALID_IMAGE_FORMAT
        await websocket.close()
        assert websocket.closed


@pytest.mark.asyncio
async def test_invalid_json(server):
    image_filters = '{"invalid_json": 1skdjfbk}'
    host, port = server
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/apply') as websocket:
        await websocket.send(image_filters)
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.INVALID_JSON
        await websocket.close()
        assert websocket.closed


@pytest.mark.asyncio
async def test_invalid_json_format(server):
    image_filters = [
        {
            "name": 100,
            "params": {}
        }
    ]
    host, port = server
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/apply') as websocket:
        await websocket.send(json.dumps(image_filters))
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.INVALID_JSON_FORMAT
        await websocket.close()
        assert websocket.closed


@pytest.mark.asyncio
async def test_filters(server):
    host, port = server
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/') as websocket:
        data = await websocket.recv()
    result = set(json.loads(data))
    expected = set(map(str, Filters))
    assert result == expected


@pytest.mark.asyncio
async def test_stat(server):
    host, port = server
    image_filters = [
        {
            "name": Filters.SEPIA.value,
            "params": {}
        },
        {
            "name": Filters.BRIGHT.value,
            "params": {
                "coefficient": 1.5
            }
        },
    ]
    source_image = read_sample('server_source.png')
    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/apply') as websocket:
        await websocket.send(json.dumps(image_filters))
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.OK

        await websocket.send(source_image)
        response = await websocket.recv()
        assert json.loads(response)["status"] == StatusCodes.OK

        await websocket.recv()

    async with websockets.connect(f'ws://{host}:{port}/api/v1/filters/stat') as websocket:
        data = await websocket.recv()
    stat = json.loads(data)
    now = datetime.datetime.now().date().isoformat()
    for date, value in stat.items():
        if date == now:
            assert value > 0
        else:
            assert value == 0

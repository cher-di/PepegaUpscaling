import argparse
import os

from .server import Server
from .database import Database


def parse_args() -> dict:
    parser = argparse.ArgumentParser('PepegaUpscaling')
    parser.add_argument('host',
                        help='Host')
    parser.add_argument('port',
                        help='Port',
                        type=int)
    parser.add_argument('database',
                        help='Path to SQLite database')
    return vars(parser.parse_args())


def main():
    args = parse_args()

    if not os.path.exists(args['database']):
        raise FileNotFoundError(args['database'])
    database = Database(args['database'])

    server = Server(args['host'], args['port'], database)
    try:
        print('Start server...')
        server.run()
    except KeyboardInterrupt:
        print('Stop server...')


if __name__ == '__main__':
    main()

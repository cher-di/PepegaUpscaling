import argparse
import os

from pepegaupscaling.database import create_database


def parse_args():
    parser = argparse.ArgumentParser('Create database')
    parser.add_argument('path',
                        help='Path to database')
    parser.add_argument('-d', '--delete',
                        dest='delete',
                        help='Delete database if exists',
                        action='store_true')
    return vars(parser.parse_args())


def main():
    args = parse_args()

    if os.path.exists(args['path']):
        print('Database exists')
        if args['delete']:
            print('Delete database')
            os.remove(args['path'])
        else:
            raise FileExistsError(args['path'])

    create_database(args['path'])

    print('Database created!')


if __name__ == '__main__':
    main()

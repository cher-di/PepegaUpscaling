import os

TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)
TEST_DATA_ROOT = os.path.join(TEST_ROOT, 'data')


def read_file_binary(filepath: str) -> bytes:
    with open(filepath, 'rb') as file:
        return file.read()


def read_sample(filename: str) -> bytes:
    filepath = os.path.join(TEST_DATA_ROOT, filename)
    return read_file_binary(filepath)

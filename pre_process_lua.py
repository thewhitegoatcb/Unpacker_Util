import pathlib
import logging

def strip_fs_lua_header(path: pathlib.Path) -> bool:
    import struct

    data = None
    with open(path, 'rb') as file:
        data = file.read()

    [size] = struct.unpack('<L', data[:4])
    if size + 12 != len(data):
        return False
    
    with open(path, 'wb') as file:
        file.write(memoryview(data)[12:])

    return True

def resolve_file_conflict(path_a: pathlib.Path, path_b: pathlib.Path):
    import filecmp

    return filecmp.cmp(path_a, path_b, False)


def recursive_gather_files(path, unique_files: dict):
    for file_dir in path.iterdir():
        if file_dir.is_file():
            if file_dir.suffix != ".lua":
                continue

            if file_dir.stem in unique_files:
                conflicting_file = unique_files[file_dir.stem]
                if resolve_file_conflict(file_dir, conflicting_file):
                    logging.warning(f'Removing duplicate file! "{str(file_dir)}"')
                    file_dir.unlink()
                else:
                    logging.warning(f'File conflict with different files! "{str(file_dir)}" - "{conflicting_file}"')
            else:
                unique_files[file_dir.stem] = file_dir

        if file_dir.is_dir():
            recursive_gather_files(file_dir, unique_files)

def strip_fs_lua_header_files(files: list[pathlib.Path]):
    for file in files:
        if strip_fs_lua_header(file):
            logging.debug(f'Removed header for flie "{str(file)}"')
        else:
            logging.warning(f'Couldn\'t remove header for flie "{str(file)}" , already removed?')

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
                    prog='Pre porcess lua',
                    description='Pre processes lua files for decompiling by removing fatshark lua headers and delete duplicate files')
    parser.add_argument('input_path', type=pathlib.Path)
    
    return parser.parse_args()

def pre_process_lua(input_path):
    unique_files = dict()
    recursive_gather_files(input_path, unique_files)
    strip_fs_lua_header_files(unique_files.values())

if __name__ == '__main__':
    options = parse_args()
    input_path = options.input_path

    pre_process_lua(input_path)

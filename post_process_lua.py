import pathlib
import io
import logging

def extract_path(file: io.RawIOBase):
    chunkname = file.readline()
    parts = chunkname.split('chunkname: @')

    if len(parts) != 2:
        return None
    
    return parts[1].strip()

def process(path, output_path):
    for file_dir in path.iterdir():
        if file_dir.is_file():
            if file_dir.suffix != ".lua":
                continue

            with open(file_dir, 'r') as file:
                file_dest = extract_path(file)

                if file_dest is None:
                    logging.warning(f'Couldn\'t get the chunkname of "{str(file_dir)}" ,skipping!')
                    continue
                
                dest_path = output_path / file_dest
                dest_folder = dest_path.parent
                dest_folder.mkdir(parents=True, exist_ok=True)

                file.readline()
                data = file.read()
                with open(dest_path, 'w') as out_h:
                    out_h.write(data)
                
                logging.info(f'Moved file "{str(file_dir)}" to "{str(dest_path)}"')

        elif file_dir.is_dir():
            process(file_dir, output_path)

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
                    prog='Post porcess lua',
                    description='Post processes lua files after decompiling by renaming them and placing in the original directory')
    parser.add_argument('input_path', type=pathlib.Path)
    parser.add_argument('output_path', type=pathlib.Path)

    return parser.parse_args()

def post_process_lua(input_path, output_path):
    process(input_path, output_path)

if __name__ == '__main__':
    options = parse_args()

    post_process_lua(options.input_path, options.output_path)
    
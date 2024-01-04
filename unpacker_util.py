import logging
import pathlib

#https://stackoverflow.com/a/11541495
def is_file_exists(x):
    import argparse

    if not (file := pathlib.Path(x)).is_file():
        raise argparse.ArgumentTypeError(f'"{str(x)}" does not exist')
    return file

def is_dir_exists(x):
    import argparse

    if not (file := pathlib.Path(x)).is_dir():
        raise argparse.ArgumentTypeError(f'"{str(x)}" does not exist')
    return file

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
                    prog='Unpacker Utility',
                    description='Batch unpacking for bundle unpacker')
    
    parser.add_argument('bundles_path', type=is_dir_exists)
    parser.add_argument('--output_path', '-o', type=pathlib.Path, default='./output')
    parser.add_argument('--unpacker_path', '-u', type=is_file_exists, default='./unpacker.exe')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--clear', '-c', action='store_true', help='Clear the output folder before any operation')

    subparsers = parser.add_subparsers(dest='subparser')
    unpack_parser = subparsers.add_parser('unpack')
    unpack_parser.add_argument('--flatten', '-f', action='store_true')
    unpack_parser.add_argument('--pass_args', '-p', nargs='+', default=[])

    decompile_parser = subparsers.add_parser('decompile')
    decompile_parser.add_argument('--decompiler_path', '-d', type=is_file_exists, default='./luajit-decompiler-v2.exe')
    
    return parser.parse_args()
    
def extract_files(bundles_path, unpacker_path, output_path, unpacker_extra_args=[], flatten=False):
    import subprocess
    from bundle_database import BundleDatabase

    bundle_database_path = bundles_path / 'bundle_database.data'

    if not bundle_database_path.is_file():
        logging.error(f'Couldn\'t find "bundle_database.data" at "{str(bundles_path)}" aborting...')
        raise FileNotFoundError(bundle_database_path)
    
    pass_args = ''
    for arg in unpacker_extra_args:
        pass_args += str(arg) + ' '
    
    with open(bundles_path / 'bundle_database.data', 'rb') as file:
        bundle_database = BundleDatabase(file)
        bundle_packs = bundle_database.parse()

        for i, bundle_pack in enumerate(bundle_packs):
            if len(bundle_pack) == 0:
                continue
            
            mkdir_needed = True
            output_dir = output_path if flatten else output_path / bundle_pack[0].name
            
            for bundle in bundle_pack:
                bundle_path: pathlib.Path = bundles_path / bundle.name
                if bundle_path.exists() and bundle_path.is_file():
                    if mkdir_needed:
                        output_dir.mkdir(parents=True, exist_ok=True)
                        mkdir_needed = False
                else:
                    logging.warning(f'Bundle: "{bundle.name}" is missing, skipping...')
                    continue
                
                unpacker_cmdline = f'"{str(unpacker_path)}" extract --skip-patches {pass_args} "{str(bundle_path)}" "{str(output_dir)}"'

                logging.info(f'Extracting ({i}/{len(bundle_packs)}) - "{bundle.name}"')
                logging.debug(f'Running unpacker with {unpacker_cmdline}')
                subprocess.run(unpacker_cmdline)

            if not flatten and not mkdir_needed and output_dir.exists() and not any(output_dir.iterdir()):
                logging.info(f'Removing empty dir "{output_dir}"')
                output_dir.rmdir()

def extract_decompile_lua(bundles_path, unpacker_path, decompiler_path, output_path):
    from pre_process_lua import pre_process_lua
    from post_process_lua import post_process_lua
    import tempfile
    import subprocess

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)

        logging.info(f'Extracting into temp "{str(tmpdir_path)}"...')
        extract_files(bundles_path, unpacker_path, tmpdir_path, ['-i', '*.lua'])

        logging.info(f'Pre processing lua files...')
        pre_process_lua(tmpdir_path)

        logging.info(f'Decompiling...')
        subprocess.run([str(decompiler_path), tmpdir, '-o', tmpdir])

        logging.info(f'Moving to the tree at "{str(output_path)}"...')
        post_process_lua(tmpdir_path, output_path)

        logging.info(f'Done extraction and decompilation!')

if __name__ == '__main__':
    options = parse_args()
    logging.basicConfig(level= (logging.DEBUG if options.verbose else logging.INFO))

    if options.clear and options.output_path.is_dir():
        logging.info(f'Removing output directory "{str(options.output_path)}"')
        options.output_path.rmdir()
    
    if options.subparser == 'unpack':
        extract_files(options.bundles_path, options.unpacker_path, options.output_path, options.pass_args, options.flatten)
    elif options.subparser == 'decompile':
        extract_decompile_lua(options.bundles_path, options.unpacker_path, options.decompiler_path, options.output_path)

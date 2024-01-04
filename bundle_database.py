import struct
import io
import logging

class BundleMetaInfo:
    def __init__(self, id, name, stream_name, platform_specific, filetime, hash) -> None:
        self.id = id
        self.name = name
        self.stream_name = stream_name
        self.platform_specific = platform_specific
        self.filetime = filetime
        self.hash = hash

    def __repr__(self) -> str:
        return f'id: {self.id:X}, name: {self.name}, stream_name: {self.stream_name}, platform_specific: {self.platform_specific}, filetime: {self.filetime}'
    
class BundleDatabase:
    def __init__(self, file: io.RawIOBase) -> None:
        self.file = file
        self.bundle_packs = []

    def _read_struct(self, format):
        size = struct.calcsize(format)
        data = self.file.read(size)
        return struct.unpack(format, data)
    
    def _read_fs_str(self):
        [str_len] = self._read_struct('<L')
        byte_str = self.file.read(str_len)
        return byte_str.decode()

    def parse(self):
        version, size = self._read_struct('<LL')
        logging.info(f"Parsing bundle database with version: {version} with {size} entries")

        bundle_packs = []
        for i in range(size):
            [bundle_id, bundle_size] = self._read_struct('<QL')
            bundles = []
            for j in range(bundle_size):
                [bundle_unk] = self._read_struct('<l')
                if bundle_unk != 4:
                    continue

                bundle_name = self._read_fs_str()
                bundle_stream_name = self._read_fs_str()
                [bundle_platform_specific] = self._read_struct('<B')
                bundle_hash = self.file.read(20)
                [bundle_filetime] = self._read_struct('<Q')

                bundles.append(BundleMetaInfo(bundle_id, bundle_name, bundle_stream_name, bundle_platform_specific, bundle_filetime, bundle_hash))
            bundle_packs.append(bundles)

        self.bundle_packs = bundle_packs
        return self.bundle_packs

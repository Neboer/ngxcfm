from os import walk, path, readlink
from os.path import isdir, isfile, join, split, splitext, islink
from typing import Literal

from ._os_style import optional_style_default_current_os
from ..log import logger
from pydos2unix import dos2unix, unix2dos

# https://stackoverflow.com/a/7392391/10796896
_text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})

def is_content_binary(input_content: bytes) -> bool:
    return bool(input_content.translate(None, _text_chars))

@optional_style_default_current_os
def recursive_convert_line_endings_style_in_dir(dir_path: str, style: Literal["win", "posix"]):
    for root, dirs, files in walk(dir_path):
        for file in files:
            file_path = path.join(root, file)
            if isfile(file_path) and not islink(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                if is_content_binary(content):
                    logger.warning(f"Skipping binary file: {file_path}")
                    continue

                if style == 'win':
                    content = unix2dos(content)
                elif style == 'posix':
                    content = dos2unix(content)

                with open(file_path, 'wb') as f:
                    f.write(content)

                logger.debug(f"Converted line endings in {file_path} to {style}")
            else:
                logger.debug(f"Skipping path {file_path} for its not a file.")

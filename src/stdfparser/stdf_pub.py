import logging
from typing import Tuple
from .util import Publisher, FilePointer, unp


class StdfPub(Publisher):
    def __init__(self, stdf_path: str):
        Publisher.__init__(self)
        self.stdf_path = stdf_path

    async def parse(self):
        with FilePointer(self.stdf_path) as fp:
            while True:
                try:
                    s_len, typ, sub, header_buf = self._get_header(fp)
                    buf = fp.read(s_len)
                    if len(buf) != s_len:
                        raise BufferError('Not enough data read...')
                    await self.dispatch((typ, sub, header_buf, buf))

                except EOFError:
                    logging.debug("Parse complete...")
                    break

                except BufferError:
                    logging.error("Incomplete log...")
                    break
        # kill subscriber
        await self.dispatch(None)

    @staticmethod
    def _get_header(fd) -> Tuple[int, int, int, bytes]:
        header_buf = fd.read(4)  # STDF header is 4 bytes long
        if len(header_buf) == 0:
            raise EOFError

        elif len(header_buf) != 4:
            raise BufferError

        s_len = unp('H', header_buf[0:2])
        typ = header_buf[2]
        sub = header_buf[3]
        return s_len, typ, sub, header_buf

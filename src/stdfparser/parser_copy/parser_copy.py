import gzip
import re
from Semi_ATE import STDF
from parser_base import ParserBase


class ParserCopy(ParserBase):
    def __init__(self):
        ParserBase.__init__(self)

    def parse(self, file_path: str):
        if file_path.endswith(".gz"):
            fd = gzip.open(file_path)
        else:
            fd = open(file_path, "rb")
        f_out_path = file_path.replace(".stdf.gz", "_mod.stdf")
        assert file_path != f_out_path
        self.f_out = open(f_out_path, "wb")

        while True:
            r = self._get_header(fd)
            if r == 'EOF':  # No data in file anymore, break
                break
            else:
                slen, (typ, sub), head_buf = r  # buf length and type,sub is returned

            ori_buf = fd.read(slen)
            assert len(ori_buf) == slen, 'Not enough data read from %s for record %s' % (file_path, str(self.Rec_Dict[(typ, sub)]))
            buf = ori_buf[:]
            self.process(buf)
            self._take((typ, sub), head_buf, ori_buf)

        self.f_out.close()

    def _take(self, typ_sub, head_buf, buf):
        if self.Cur_Rec.name == "Dtr":

            text = self.data["TEXT_DAT"].decode()

            if re.search(r"COND:.*,alarm=", text):
                print(text)
                return
            elif re.search("COND: V18_BF=0.00V", text):
                dtr = STDF.DTR()
                dtr.set_value("TEXT_DAT", "/* CHARINFO py_short_v11 alarm (CURRENT_CLAMP) */")
                print(dtr)
                self.f_out.write(dtr.__repr__())

        self.f_out.write(head_buf)
        self.f_out.write(buf)


if __name__ == '__main__':
    c = ParserCopy()
    c.parse(r"C:\Users\nxf79056\Downloads\T6K160.00_STRV_T6K160-06G5_20220401102358.stdf.gz")

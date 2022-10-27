import re
from .stdf_sub import StdfSub


class StdfSubFilter(StdfSub):
    def __init__(self, name: str, mod_stdf_path: str):
        StdfSub.__init__(self, name)
        self.fp = open(mod_stdf_path, "wb")

    def post_process(self):
        if self.cur_rec.name == "Dtr":
            text = self.data["TEXT_DAT"].decode()
            if re.search(r"COND:.*(wmark|alarm)=", text) or re.search("CHARINFO", text):
                print(text)
                return

        self.fp.write(self._head_buf)
        self.fp.write(self._buf)

    def on_listen_end(self):
        self.fp.close()

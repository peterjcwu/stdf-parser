import os
from stdf_sub import StdfSub


class StdfSubTxt(StdfSub):
    def __init__(self, name: str, mod_stdf_path: str):
        StdfSub.__init__(self, name)
        self.fp = open(mod_stdf_path, "w", newline="")

    def _take(self):
        self.fp.write(f'======= {self.cur_rec.name} =======' + os.linesep)
        for field_name, data_type in self.cur_rec.fieldMap:
            self.fp.write(f'< {self.cur_rec.name} >  :  {field_name} ---> {self.data[field_name]}' + os.linesep)

    def on_listen_end(self):
        self.fp.close()

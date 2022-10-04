import re
from stdf_sub import StdfSub


class StdfSubWlanSweep(StdfSub):
    def __init__(self, name: str):
        StdfSub.__init__(self, name)
        self._cache = {}  # site -> test_text -> [list of (tag, val)]
        self._tag = {}  # site -> tag

    def _rec_filter(self) -> bool:
        return self.cur_rec.name in {"Ptr", "Dtr", "Prr"}

    def _take(self):
        if self.cur_rec.name == "Dtr":
            self.dtr_handler()

        elif self.cur_rec.name == "Prr":
            self.prr_handler()

        elif self.cur_rec.name == "Ptr":
            self.ptr_handler()

    def dtr_handler(self):
        # handle tag
        text = self.data["TEXT_DAT"].decode()
        m = re.search(r"Log:.*\[(?P<other>.*)\]", text, re.I)
        if m:
            other = m.group("other")
            m2 = eval("{" + other + "}")
            self._tag = {**m2}

    def ptr_handler(self) -> None:
        site = self.data["SITE_NUM"]
        text = self.data["TEST_TXT"].decode()
        result = self.data["RESULT"]

        if re.search("cont_pmu|dc_ioleakage|p_lkg|px_short|fx_jtag", text):
            return

        if site not in self._cache:
            self._cache[site] = {}
        if text not in self._cache[site]:
            self._cache[site][text] = []

        self._cache[site][text].append((self._tag.get(site), result))

    def prr_handler(self) -> None:
        print(self.data)

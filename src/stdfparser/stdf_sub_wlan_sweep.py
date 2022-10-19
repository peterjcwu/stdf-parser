import re
import csv
from typing import List
from stdf_sub import StdfSub


class StdfSubWlanSweep(StdfSub):
    def __init__(self, name: str):
        StdfSub.__init__(self, name)
        self._cache1: List[dict] = []  # {"site": [], "test_text": [], "power": [], "tag": [], "val": []}
        self._cache2: List[dict] = []  # {"site": [], "test_text": [], "power": [], "tag": [], "val": [], "die_id": []}
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
        m = re.search(r"Log:.*\[(?P<other>.*)]", text, re.I)
        if m:
            other = m.group("other")
            self._tag = eval("{" + other + "}")

    def ptr_handler(self) -> None:
        def get_power_val(t) -> float:
            m = re.search(r"_m(?P<power>\d+)", t)
            return float(m.group("power")) * -1 if m else float("nan")

        def get_suite(t) -> str:
            return "_".join(t.split("_")[:8])

        def get_pdt(t) -> str:
            return t.split("_")[-1]

        site = self.data["SITE_NUM"]
        text = self.data["TEST_TXT"].decode()
        result = self.data["RESULT"]

        if re.search("cont_pmu|dc_ioleakage|p_lkg|^p[xy]|^fx?_|a_evmXrx|a_cal", text):
            return

        self._cache1.append({"site": site,
                             "text": text,
                             "power": get_power_val(text),
                             "tag": self._tag.get(site, ""),
                             "result": result,
                             "suite": get_suite(text),
                             "pdt": get_pdt(text),
                             })

    def prr_handler(self) -> None:
        print(self.data)

    def on_listen_end(self):
        with open(r"c:\tmp\out.csv", "w", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=self._cache1[0].keys())
            writer.writeheader()
            for row in self._cache1:
                writer.writerow(row)

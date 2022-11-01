import re
from collections import defaultdict
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
from .stdf_sub import StdfSub
from . import DBConn


class BaseRow:
    def as_dict(self):
        return dict(self.__dict__)


class MirRow(BaseRow):
    def __init__(self, d: dict, stdf_name: str):
        self.stdf_name = stdf_name
        self.start_t = datetime.fromtimestamp(d["START_T"])
        self.node_name = d["NODE_NAM"].decode()
        self.job_name = d["JOB_NAM"].decode()
        self.upload_t = datetime.utcnow()


class PrrRow(BaseRow):
    def __init__(self, d: dict, mir_id: ObjectId):
        self.mir_id = mir_id
        self.site: int = d["SITE_NUM"]
        self.num_test: int = d["NUM_TEST"]
        self.x: int = d["X_COORD"]
        self.y: int = d["Y_COORD"]
        self.sb: int = d["SOFT_BIN"]
        self.hb: int = d["HARD_BIN"]
        self.part_id = int(d["PART_ID"].decode())


class PtrRow(BaseRow):
    def __init__(self, d: dict, tag: str, suite: str):
        self.tag: str = tag
        self.suite: str = suite
        self.mir_id: Optional[ObjectId] = None
        self.prr_id: Optional[ObjectId] = None
        self.t_num: int = d["TEST_NUM"]
        self.text: str = d["TEST_TXT"].decode()
        self.site: int = d["SITE_NUM"]
        self.v: float = d['RESULT']
        self.lo_lim: float = d['LO_LIMIT']
        self.hi_lim: float = d['HI_LIMIT']
        self.unit: str = d['UNITS'].decode()

    def update_key(self, mir_id: ObjectId, prr_id: ObjectId):
        self.mir_id = mir_id
        self.prr_id = prr_id
        return self

    def __repr__(self):
        return f"{self.t_num}:{self.text}:{self.v}"


class StdfSubWlanSweep(StdfSub):
    def __init__(self, db_conn: DBConn):
        StdfSub.__init__(self, db_conn.stdf_name)
        self.db_conn = db_conn
        self.mir_id = ObjectId()
        self.cur_tag = defaultdict(dict)  # site -> tag
        self.cur_suite: str = ""
        self._die_id: int = 0
        self._cache: Dict[int, List[PtrRow]] = defaultdict(list)
        self._previous_rec_name: str = ""
        self._handlers: dict = {
            "Ptr": self.ptr_handler,
            "Dtr": self.dtr_handler,
            "Prr": self.prr_handler,
            "Mir": self.mir_handler,
        }

    def _rec_filter(self) -> bool:
        return self.cur_rec.name in self._handlers.keys()

    def post_process(self):
        if self.cur_rec.name in self._handlers.keys():
            self._handlers[self.cur_rec.name]()

    def on_listen_end(self):
        print(f"parse stdf {self.db_conn.stdf_name} successfully; mir_id={self.db_conn.get_mir_id()}")

    def mir_handler(self):
        res = self.db_conn.collection_mir.insert_one(MirRow(self.data, self.name).as_dict())
        self.mir_id = res.inserted_id
        self._previous_rec_name = "Mir"

    def dtr_handler(self) -> None:
        def log_handler(key: str, site_val: str) -> None:
            if self._previous_rec_name != "Log":  # todo: change to looking for Log:Reset
                self.cur_tag.clear()
            for site, val in eval("{" + site_val + "}").items():
                self.cur_tag[site][key] = val
            self._previous_rec_name = "Log"

        def test_suite_handler(test_suite_name: str):
            self.cur_suite = test_suite_name
            self._previous_rec_name = "Suite"

        # Log
        text = self.data["TEXT_DAT"].decode()
        if m := re.search(r"Log:(?P<field>\w+)=\[(?P<site_val>.*)]", text):
            log_handler(m.group("field"), m.group("site_val"))
        # Test suite
        elif re.search(r"^Main\.\w+", text):
            test_suite_handler(text)

    def ptr_handler(self) -> None:
        site = self.data["SITE_NUM"]
        self._cache[site].append(PtrRow(self.data, self._get_tag_str(site), self.cur_suite))
        self._previous_rec_name = "Ptr"

    def _get_tag_str(self, site: int) -> str:
        if site not in self.cur_tag:
            return ""
        tags = []
        for key in sorted(self.cur_tag[site].keys()):
            v = self.cur_tag[site][key]
            if type(v) == float:
                v = "{:.4f}".format(v)
            tags.append(f"{key}={v}")
        return ";".join(tags)

    def prr_handler(self) -> None:
        prr_row = PrrRow(self.data, self.mir_id)
        res = self.db_conn.collection_prr.insert_one(prr_row.as_dict())
        prr_id = res.inserted_id

        ptr_row_dicts = [c.update_key(self.mir_id, prr_id).as_dict()
                         for c in self._cache.get(prr_row.site, [])]

        if len(ptr_row_dicts) > 0:
            self.db_conn.collection_ptr.insert_many(ptr_row_dicts, ordered=False)

        self._previous_rec_name = "Prr"

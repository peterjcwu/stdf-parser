import os
import re
import pandas as pd
from bson.objectid import ObjectId
from typing import List, Optional, Tuple
from stdfparser import StdfPub, StdfSubEmbeddedDoc, DBConn, parse
from stdfparser.util import get_stdf_name, is_num


class Fetch:
    def __init__(self, db_conn, folder_path: str, force: bool = False):
        self._db_conn = db_conn
        self._stdf_paths: List[str] = self.get_stdf_paths(folder_path)
        self._force = force

    @staticmethod
    def get_stdf_paths(folder_path: str) -> List[str]:
        stdf_paths = []
        for cur_dir, dirs, file_names in os.walk(folder_path):
            for file_name in file_names:
                stdf_paths.append(os.path.join(cur_dir, file_name))
        return stdf_paths

    @property
    def stdf_name_mir_id(self) -> List[Tuple[str, ObjectId]]:
        stdf_name_mir_id_list = []
        for stdf_path in self._stdf_paths:
            stdf_name = get_stdf_name(stdf_path)

            # force update
            if self._force:
                parse(StdfPub(stdf_path), StdfSubEmbeddedDoc(self._db_conn, stdf_path))

            # query
            rows = [row for row in self._db_conn.collection_mir.find({
                "stdf_name": stdf_name,
                "finish_t": {"$exists": True}
            }).sort([("_id", -1)]).limit(1)]
            if len(rows) == 0:
                parse(StdfPub(stdf_path), StdfSubEmbeddedDoc(self._db_conn, stdf_path))

            # query again
            rows = [row for row in self._db_conn.collection_mir.find({
                "stdf_name": stdf_name,
                "finish_t": {"$exists": True}
            }).sort([("_id", -1)]).limit(1)]

            if len(rows) > 0:
                stdf_name_mir_id_list.append((stdf_name, rows[0]["_id"]))

        return stdf_name_mir_id_list

    @staticmethod
    def get_filter_cond(value_min: str, value_max: str) -> list:
        cond = []
        if is_num(value_min):
            cond.append({"$gte": ["$$vt_list.v", float(value_min)]})
        if is_num(value_max):
            cond.append({"$lte": ["$$vt_list.v", float(value_max)]})
        return cond

    def get_df(self, test_text: str, value_min: str, value_max: str, aggregate: str, extra_pipeline: list = None):
        rows = []
        # loop stdf
        for stdf_name, mir_id in self.stdf_name_mir_id:
            filter_cond = self.get_filter_cond(value_min, value_max)
            # loop part-id
            for row in self.get_rows(mir_id, test_text, filter_cond, aggregate, extra_pipeline):
                row["pout"] = self.get_pout(row.get("text", ""))
                row["id"] = "_".join([stdf_name.split("_")[-1], str(row.get("part_id"))])
                row["stdf"] = stdf_name
                # unwind tag
                for token in row.get("tag", "").split(";"):
                    kv = token.split("=")
                    if len(kv) == 2:
                        k, v = kv
                        row[k.strip().lower()] = float(v) if is_num(v) else v.strip()
                rows.append(row)
        return pd.DataFrame(rows)

    def get_rows(self, mir_id: ObjectId, test_text: str, filter_cond: list, aggregate: str, extra_pipeline: list):
        pipelines = [
            {"$match": {"mir_id": mir_id, "text": re.compile(pattern=test_text)}},
            {"$unwind": "$rows"},
            {"$match": {"rows": {"$ne": None}}},
            {"$addFields": {  # value filter
                "v": {
                    "$filter": {
                        "input": "$rows.vt_list",
                        "as": "vt_list",
                        "cond": {"$and": filter_cond},
                    }
                }}},
            {"$lookup": {"from": "prr", "localField": "rows.prr_id", "foreignField": "_id", "as": "prr"}},
            {"$unwind": "$prr"},
            {"$unwind": "$v"},
            {"$group": {
                "_id": {
                    "tag": "$v.t",
                    "text": "$text",
                    "part_id": "$prr.i",
                },
                "t_num": {"$first": "$t_num"},
                f"{aggregate}": {f"${aggregate}": "$v.v"},
                "count": {"$count": {}},
                "site": {"$first": "$prr.site"},
            }},
            {"$project": {
                "_id": 0,
                "tag": "$_id.tag",
                "text": "$_id.text",
                "part_id": "$_id.part_id",
                "t_num": 1,
                f"{aggregate}": 1,
                "count": 1,
                "site": 1,
            }},
        ]
        if extra_pipeline is not None:
            pipelines += extra_pipeline

        return [row for row in self._db_conn.collection_ptr.aggregate(pipelines)]

    @staticmethod
    def get_pout(t: str) -> Optional[float]:
        m = re.search(r"_(?P<pout>[pm]\d+)", t)
        if not m:
            return
        pout = m.group("pout")
        pout_val = pout[1:]
        if pout.startswith("m"):
            return -float(pout_val)
        return float(pout_val)


if __name__ == '__main__':
    db_name = os.path.basename((os.getcwd()))
    folder = os.path.join(__file__, os.pardir, os.pardir, os.pardir, os.pardir, "lab", "stdf")
    df = Fetch(DBConn(db_name), folder).get_df(  #
        test_text="_rssi$",
        value_min="-100",
        value_max="",
        aggregate="min")
    print(os.getcwd())

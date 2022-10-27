from typing import Optional, List
from bson import ObjectId
from stdfparser.db.db_conn import DBConn


class QueryV11Sweep:
    def __init__(self, db_type: str, project_name: str, stdf_name: str):
        self.project_name = project_name
        self.db = DBConn.get_client(db_type)[project_name]
        self.stdf_name = stdf_name

    def get_df(self, suite_name: str):
        for row in self.db["mir"].aggregate([
            # lookup prr in stdf
            {"$match": {"stdf_name": self.stdf_name}},
            {"$sort": {"_id": -1}},
            {"$limit": 1},
            {"$lookup": {"from": "prr", "localField": "_id", "foreignField": "mir_id", "as": "prr"}},
            {'$unwind': {'path': '$prr'}},
            # lookup ptr for each prr
            {"$lookup": {"from": "ptr", "localField": "prr._id", "foreignField": "prr_id", "as": "ptr"}},
            {'$unwind': {'path': '$ptr'}},
            # filter
            {"$match": {"ptr.suite": suite_name}},
            {"$addFields": {"tokens": {"$split": ["$ptr.text", "_"]}}},
            {"$match": {"tokens.10": "rssi"}},
            {"$addFields": {"pout": {"$toDouble": {"$substr": [{"$arrayElemAt": ["$tokens", 9]}, 1, -1]}}}},  # m<pout>
            {"$match": {"ptr.v": {"$gt": -100}}},  # good die
            {"$group": {
                "_id": {
                    "part_id": "$prr.part_id",
                    "site": "$prr.site",
                    "tag": "$ptr.tag",
                    "pout": "$pout"
                },
                "rssi_min": {"$min": "$ptr.v"},
                "count": {"$count": {}},
            }},
        ]):
            print(row)

    def plot(self, suite_name: str):
        df = self.get_df(suite_name)

    @property
    def mir_id(self) -> Optional[ObjectId]:
        for row in self.db["mir"].find({"stdf_name": self.stdf_name}).sort([("_id", -1)]).limit(1):
            return row["_id"]
        raise KeyError(f"stdf_name: 'f{self.stdf_name}' does not exist")

    @property
    def prr_id_list(self) -> Optional[List[ObjectId]]:
        return [row["_id"] for row in self.db["prr"].find({"mir_id": self.mir_id})]


if __name__ == '__main__':
    QueryV11Sweep("ENG", "redfinch", "sweep_with_svc")\
        .plot("Main.WLAN.RFU_RX_char.a_gainXrx_11axmcs0_2437_x_x__6dbgstepbw20")

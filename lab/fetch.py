from typing import List
from stdfparser import DBConn


def get_records_v11(db_conn: DBConn, suite_name: str) -> List[dict]:
    rows = [row for row in db_conn.collection_mir.aggregate([
        # lookup prr in stdf
        {"$match": {"stdf_name": db_conn.stdf_name}},
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
        {"$project": {
            "_id": 0,
            "part_id": "$_id.part_id",
            "site": "$_id.site",
            "tag": "$_id.tag",
            "pout": {"$multiply": ["$_id.pout", -1]},
            "rssi_min": 1,
            "count": 1,
        }},
        {"$sort": {"site": 1}},
    ])]
    # unwind tag
    for row in rows:
        for token in row.pop("tag", "").split(";"):
            kv = token.split("=")
            if len(kv) != 2:
                continue
            k, v = kv
            row[k.lower()] = float(v)

    return rows

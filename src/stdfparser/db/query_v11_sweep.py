import pandas as pd
from pymongo import MongoClient
client = MongoClient("mongodb://localhost")
db = client["redfinch"]


def get_df(stdf_name: str, suite_name: str):
    rows = [row for row in db["mir"].aggregate([
        # lookup prr in stdf
        {"$match": {"stdf_name": stdf_name}},
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
            "pout": "$_id.pout",
            "rssi_min": 1,
            "count": 1,
        }}
    ])]
    # unwind tag
    for row in rows:
        for token in row.pop("tag", "").split(";"):
            kv = token.split("=")
            if len(kv) != 2:
                continue
            k, v = kv
            row[k] = float(v)
    return rows


records = get_df("sweep_with_svc", "Main.WLAN.RFU_RX_char.a_gainXrx_11axmcs0_2437_x_x__6dbgstepbw20")
df = pd.DataFrame.from_records(records)


from lets_plot import *
LetsPlot.setup_html()
LetsPlot.set_theme(theme_light())



sub_recs_v11 = [[rec for rec in records if rec["V11"] == v11] for v11 in df.V11.unique()]


# part_id
pout = [row["pout"] for row in sub_recs_v11[0]]
rssi_min = [row["rssi_min"] for row in sub_recs_v11[0]]
ggplot({"pout": pout, "rssi_min": rssi_min}, aes(x = "pout", y = "rssi_min")) \
    + geom_point(aes(x='pout', y='rssi_min', fill='rssi_min'), shape=21, size=3, color='white')

import os
import re
import pandas as pd
from bson.objectid import ObjectId
from dataclasses import dataclass
from typing import List, Tuple
from stdfparser import StdfPub, StdfSubWlan, DBConn, parse
from stdfparser.util import get_stdf_name


@dataclass
class QueryParam:
    stdf_name: str
    stdf_id: str
    text: str = ""


class Pipeline:
    @classmethod
    def get(cls, q: QueryParam, extra_pipeline: str, _pipelines: list=None) -> list:
        pipeline = [
            {"$match": {"stdf_name": q.stdf_name.split(".")[0]}},
            {"$sort": {"_id": -1}},
            {"$limit": 1},
            {"$lookup": {"from": "prr", "localField": "_id", "foreignField": "mir_id", "as": "prr"}},
            {'$unwind': {'path': '$prr'}},
            {"$lookup": {"from": "ptr", "localField": "prr._id", "foreignField": "prr_id", "as": "ptr"}},
            {'$unwind': {'path': '$ptr'}},
            {"$addFields": {"tokens": {"$split": ["$ptr.text", "_"]}}},
        ]
        
        # tokens
        if q.text != "":
            tokens = [t for t in q.text.split("_")]
            pipeline += [{"$match": {"tokens": {"$size": len(tokens)}}}]

            for i, s in reversed([(i, s) for (i, s) in enumerate(tokens)]):
                if s.lower() not in {"", "x"}:
                    pipeline += [{"$match": {f"tokens.{i}": s}}]

        # extra_pipeline
        for p in extra_pipeline.split("+"):
            if p == "rssi_min":
                pipeline += cls.pipeline_rssi_min() + cls.pipeline_pout()
            elif p.startswith("gt"):
                t = p.split(":")
                assert(len(t) == 2)
                pipeline += cls.pipeline_gt(float(t[1]))

        pipeline += cls.piepline_id(q.stdf_id)
    
        if _pipelines is not None:
            pipeline += _pipelines
            
        return pipeline
    
    @staticmethod
    def pipeline_gt(val: float) -> List[dict]:
        return [{"$match": {"ptr.v": {"$gt": val}}}]

    @staticmethod
    def pipeline_pout() -> List[dict]:
        # require fields text and part_id
        return [
            {"$addFields": {"pout_regex":  {"$regexFind": {"input": "$text", "regex": "_m(\d+)"}}}},
            {"$addFields": {"pout_pos": {"$toDouble": {"$arrayElemAt": ["$pout_regex.captures", 0]}}}},
            {"$addFields": {"pout": {"$multiply": ["$pout_pos", -1]}}},
            {"$unset": ["pout_regex", "pout_pos"]},
            {"$match": {"pout": {"$ne": None}}},
            {"$sort": {"part_id": 1, "pout": 1}},
        ]
    
    @staticmethod
    def pipeline_rssi_min() -> List[dict]:
        return [
            {"$group": {
                "_id": {
                    "part_id": "$prr.part_id",
                    "site": "$prr.site",
                    "tag": "$tag",
                    "text": "$ptr.text"
                },
                "rssi_min": {"$min": "$ptr.v"},
                "count": {"$count": {}},
            }},
            {"$project": {
                "_id": 0,
                "part_id": "$_id.part_id",
                "site": "$_id.site",
                "tag": "$_id.tag",
                "text": "$_id.text",
                "rssi_min": 1,
                "count": 1,
            }},
        ]
    
    @staticmethod
    def piepline_id(stdf_id: str) -> List[dict]:
        return [
            {"$addFields": {"stdf_id": stdf_id}},
            {"$addFields": {
                "key": {"$concat": [
                    stdf_id, 
                    "_", 
                    {"$toString": {"$ifNull": ["$part_id", "$prr.part_id"]}}
                ]}}
            },
        ]


class Query:
    def __init__(self, db_name: str):
        self.db_conn: str = DBConn(db_name)

    def _parse(self, stdf_path: str) -> ObjectId:
        # ensure index
        self.db_conn.collection_prr.create_index("mir_id")
        self.db_conn.collection_ptr.create_index("mir_id")
        self.db_conn.collection_ptr.create_index("prr_id")
        
        if self.db_conn.get_mir_id(get_stdf_name(stdf_path)) is None:
            parse(StdfPub(stdf_path), StdfSubWlan(self.db_conn, stdf_path))
            
        return self.db_conn.get_mir_id(get_stdf_name(stdf_path))
    
    def get_df(self, params: List[QueryParam], extra_pipeline: str, _pipelines: list=None) -> pd.DataFrame:
        return pd.concat([self.get_df_one(p, extra_pipeline, _pipelines) for p in params])
        
    def get_df_one(self, p: QueryParam, extra_pipeline: str, _pipelines: list) -> pd.DataFrame:
        self._parse(os.path.join(os.path.abspath(""), p.stdf_name))
        pipeline = Pipeline.get(p, extra_pipeline, _pipelines)
        return pd.DataFrame(row for row in self.db_conn.collection_mir.aggregate(pipeline))

import os
import pymongo
from bson.objectid import ObjectId
from typing import Optional


class DBConn:
    def __init__(self, db_name: str):
        self.db_name: str = db_name
        self.client = pymongo.MongoClient(os.getenv("DB_URL"))
        self.db = self.client[db_name]
        self.collection_mir = self.db["mir"]
        self.collection_ptr = self.db["ptr"]
        self.collection_prr = self.db["prr"]
        self.stdf_name = ""

    def get_mir_id(self, stdf_name: str) -> Optional[ObjectId]:
        for row in self.collection_mir.find({"stdf_name": stdf_name}).sort([("_id", -1)]).limit(1):
            return row["_id"]

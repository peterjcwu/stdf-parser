import os
from typing import Optional

import pymongo


class DBConn:
    def __init__(self, project_name: str, stdf_path: str):
        self.project_name: str = project_name
        self.stdf_path = stdf_path
        self.client = pymongo.MongoClient(os.getenv("DB_CONN_STR"))
        self.db = self.client[project_name]
        self.collection_mir = self.db["mir"]
        self.collection_ptr = self.db["ptr"]
        self.collection_prr = self.db["prr"]

    @property
    def stdf_name(self) -> str:
        return os.path.basename(self.stdf_path).split(".")[0]

    def get_mir_id(self) -> Optional[str]:
        for row in self.collection_mir.find({"stdf_name": self.stdf_name}).sort([("_id", -1)]).limit(1):
            return str(row["_id"])
        else:
            return None

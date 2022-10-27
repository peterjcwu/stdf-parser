import os
import pymongo
_conns = {}


class DBConn:
    @staticmethod
    def get_client(name: str) -> pymongo.MongoClient:
        def _get():
            if name == "ENG":
                return pymongo.MongoClient()

            if name == "PROD":
                user = os.environ['DBUSER']
                pwd = os.environ['DBPWD']
                host = os.environ['DBHOST']
                auth_src = os.environ["DBAUTHSRC"]
                conn_str = f"mongodb://{user}:{pwd}@{host}/?authSource={auth_src}"
                return pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=3000)

        if name not in _conns:
            _conns[name] = _get()

        return _conns[name]


if __name__ == '__main__':
    client = DBConn.get_client("ENG")
    print(client.list_database_names())

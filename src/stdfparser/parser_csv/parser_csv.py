from copy import copy
from parser_base import ParserBase
from collections import defaultdict


def ptr_handler(parser, record):
    print('===========  Star of Record %s =======' % record.name)
    for i, j in parser.data.items():
        print('< %s >  :   %s ---> %s' % (record.name, str(i), str(parser.data[i])))
    parser.cache[parser.data.get("TEST_NUM")].append(copy(parser.data))


class ParserCsv(ParserBase):
    def __init__(self):
        ParserBase.__init__(self)
        self.handlers = {"Ptr": ptr_handler}
        self.cache = defaultdict(list)

    def take(self, typ_sub):
        record = self.Rec_Dict.get(typ_sub)
        if record is None or record.name not in self.handlers:
            return
        handler = self.handlers.get(record.name)
        handler(self, record)

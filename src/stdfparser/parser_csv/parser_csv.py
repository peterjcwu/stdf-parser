from copy import copy
from parser_base import ParserBase
from collections import defaultdict


def ptr_handler(parser, record):
    # print('===========  Star of Record %s =======' % record.name)
    # for i, j in parser.data.items():
    #     print('< %s >  :   %s ---> %s' % (record.name, str(i), str(parser.data[i])))
    parser.cache[parser.data.get("TEST_NUM")].append(copy(parser.data))


def prr_handler(parser, record):
    print('===========  Star of Record %s =======' % record.name)
    for i, j in parser.data.items():
        print('< %s >  :   %s ---> %s' % (record.name, str(i), str(parser.data[i])))


def dtr_handler(parser, record):
    print('===========  Star of Record %s =======' % record.name)
    for i, j in parser.data.items():
        print('< %s >  :   %s ---> %s' % (record.name, str(i), str(parser.data[i])))


class ParserCsv(ParserBase):
    def __init__(self):
        ParserBase.__init__(self)
        self.x = 0
        self.y = 0
        self.handlers = {
            "Ptr": ptr_handler,
            # "Dtr": dtr_handler,
            "Prr": prr_handler,
        }
        self.cache = defaultdict(list)

    def take(self, typ_sub):
        record = self.Rec_Dict.get(typ_sub)
        if record is None or record.name not in self.handlers:
            return
        if record.name == "Prr":
            print()
        handler = self.handlers.get(record.name)
        handler(self, record)


if __name__ == '__main__':
    c = ParserCsv()
    c.parse(r"C:\log\w228_redfinch_wlcsp_spec_search_remove_items\26819921HTOL72H_26819921HTOL72H_VER_20220627151447.stdf.gz")

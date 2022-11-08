import sys
import math
import logging
from typing import Tuple
from stdfparser.stdf_V4 import rec_dict
from stdfparser.util import Subscriber, unp, get_stdf_name


class StdfSub(Subscriber):
    def __init__(self, stdf_path: str):
        Subscriber.__init__(self)
        self.stdf_name = get_stdf_name(stdf_path)
        self.cur_rec = None
        self.data = {}
        self._head_buf: bytes = b''
        self._buf: bytes = b''

    def _process(self, message: Tuple[int, int, bytes, bytes]):
        # check if (typ, sub) is known
        typ, sub, self._head_buf, self._buf = message
        if (typ, sub) not in rec_dict:
            logging.debug(f'Unknown record type ({typ}, {sub})')
            return

        # update self.cur_rec
        self.cur_rec = rec_dict[(typ, sub)]
        if not self.rec_filter():
            return

        # lookup file-map to construct self.data
        self.data = {}  # reset
        buf = self._buf
        for field_name, data_type in self.cur_rec.fieldMap:
            v, buf = self._get_parse_func(data_type)(data_type, buf)
            self.data[field_name] = v
        self.post_process()

    def post_process(self):
        print(f'======= {self.cur_rec.name} =======')
        for field_name, data_type in self.cur_rec.fieldMap:
            print(f'< {self.cur_rec.name} >  :  {field_name} ---> {self.data[field_name]}')

    def rec_filter(self) -> bool:
        return True  # all pass

    def _get_parse_func(self, fmt):
        if fmt in {'U4', 'U1', 'U2', 'U8'}:
            return self._get_Un
        elif fmt in {'I1', 'I2', 'I4'}:
            return self._get_In
        elif fmt in {'R4', 'R8'}:
            return self._get_Rn
        elif fmt == 'Cn' or (fmt.startswith('C') and (fmt[1:].isdigit())):
            return self._get_Cn
        elif fmt in {'B1', 'Bn', 'B0'}:
            return self._get_Bn
        elif fmt.startswith('K'):
            return self._get_Kx
        elif fmt == 'N1':
            return self._get_Nn
        elif fmt == 'Dn':
            return self._get_Dn
        elif fmt == 'Vn':
            return self._get_Vn
        else:
            assert False, 'Unknown Format: %s' % fmt

    @staticmethod
    def _get_Nn(fmt, buf):
        """ Note: this function process two N1 type every time instead of one """
        r = []
        if fmt == 'N1':
            if len(buf) < 1:
                return None, ''
            else:
                tmp = unp('B', buf[0])
                r.append(tmp & 0x0F)
                r.append(tmp >> 4)
                return r, buf[1:]
        else:
            raise TypeError(f'_get_Nn: Error format: {fmt}')

    @staticmethod
    def _get_Un(fmt, buf):
        # logging.debug('In Get_Un(): %s' % format)
        if fmt == 'U4':
            if len(buf) < 4:
                return None, ''
            else:
                r = unp('I', buf[0:4])  # I -> unsigned int
                return r, buf[4:]
        elif fmt == 'U2':
            if len(buf) < 2:
                return None, ''
            else:
                r = unp('H', buf[0:2])  # H -> unsigned short
                return r, buf[2:]
        elif fmt == 'U1':
            if len(buf) < 1:
                return None, ''
            else:
                r = unp('B', buf[0:1])  # B -> unsigned char
                return r, buf[1:]
        elif fmt == "U8":
            if len(buf) < 8:
                return None, ''
            r = unp('Q', buf[0:8])  # Q -> unsigned long long
            return r, buf[8:]

        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    @staticmethod
    def _get_In(fmt, buf):
        if fmt == 'I4':
            if len(buf) < 4:
                return None, ''
            else:
                r = unp('i', buf[0:4])
                return r, buf[4:]
        elif fmt == 'I2':
            if len(buf) < 2:
                return None, ''
            else:
                r = unp('h', buf[0:2])
                return r, buf[2:]
        elif fmt == 'I1':
            if len(buf) < 2:
                return None, ''
            else:
                r = unp('b', buf[0:1])
                return r, buf[1:]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    @staticmethod
    def _get_Rn(fmt, buf):
        #        logging.debug('In Get_Rn() %s' % format)
        if fmt == 'R4':
            if len(buf) < 4:
                return None, ''
            else:
                r = unp('f', buf[0:4])
                return r, buf[4:]
        elif fmt == 'R8':
            if len(buf) < 8:
                return None, ''
            else:
                r = unp('d', buf[0:8])
                return r, buf[8:]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    @staticmethod
    def _get_Cn(fmt, buf):
        #        logging.debug('In Get_Cn(): %s' % format)
        if fmt == 'C1':
            if len(buf) < 1:
                return None, ''
            else:
                r = buf[0]
                return r, buf[1:]
        elif fmt == 'Cn':
            if len(buf) < 1:
                return None, ''
            else:
                char_cnt = buf[0]
                if len(buf) < (1 + char_cnt):
                    logging.critical(f'Cn: Not enough data in buffer: needed: {str(1 + char_cnt)},'
                                     f' actual: {str(len(buf))}')
                    return buf[1:], buf[len(buf):]
                r = buf[1:(1 + char_cnt)]
                return r, buf[(1 + char_cnt):]
        elif fmt.startswith('C') and fmt[1:].isdigit():
            if len(buf) < 1:
                return None, ''
            else:
                cnt = int(fmt[1:])
                r = buf[0:cnt]
                return r, buf[cnt:]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    @staticmethod
    def _get_Bn(fmt, buf):
        hexstring = '0123456789ABCDEF'
        if fmt in ['B1', 'B0']:
            if len(buf) < 1:
                return None, ''
            else:
                r = buf[0]
                r = '0x' + hexstring[r >> 4] + hexstring[r & 0x0F]
                #                logging.debug('B1: len(buf): %s' % str(len(buf)))
                if len(buf) == 1:
                    return r, ''
                else:
                    return r, buf[1:]
        if fmt == 'Bn':
            if len(buf) < 1:
                return None, ''
            else:
                char_cnt = unp('B', bytes([buf[0]]))
                if len(buf) < (1 + char_cnt):
                    logging.critical('Bn: Not enough data in buffer: needed: %s, actual: %s' % (str(1 + char_cnt),
                                                                                                str(len(buf))))
                    sys.exit(-1)
                r = buf[1:(1 + char_cnt)]
                tmp = '0x'
                for i in r:
                    v = unp('B', i)
                    tmp = tmp + hexstring[v >> 4] + hexstring[v & 0x0F]
                r = tmp
                return r, buf[(1 + char_cnt):]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    @staticmethod
    def _get_Dn(fmt, buf):
        if fmt == 'Dn':
            if len(buf) < 1:
                return None, ''
            else:
                dlen = unp('H', buf[0:2])
                buf = buf[2:]
                r = []
                dbyt = int(math.ceil(dlen / 8.0))
                assert len(buf) >= dbyt
                for i in range(dbyt):
                    tmp = unp('B', buf[i])
                    for j in range(8):
                        r.append((tmp >> j) & 0x01)
                return r, buf[dbyt:]

    def _get_Kx(self, fmt, buf):
        # first, parse the format to find out in which field of the record defined the length of the array
        assert fmt.startswith('K'), f'In Get_Kx(): format error: {fmt}'
        assert len(fmt) == 4 or len(fmt) == 5
        # assume format = 'K3U4' or 'K13U4', then item_format = 'U4'
        item_format = fmt[-2:]
        # then index_cnt = 3 or 13
        index_cnt = int(fmt[1:-2])
        cnt = self.data[self.cur_rec.fieldMap[index_cnt][0]]
        r = []
        func = self._get_parse_func(item_format)
        if item_format == 'N1':
            cnt = int(math.ceil(cnt / 2.0))
            for i in range(cnt):
                item, buf = func(item_format, buf)
                r.append(item[0])
                r.append(item[1])
            return r, buf
        else:
            for i in range(cnt):
                item, buf = func(item_format, buf)
                r.append(item)
            return r, buf

    def _get_Vn(self, fmt, buf):
        data_type = ['B0', 'U1', 'U2', 'U4', 'I1', 'I2', 'I4',
                     'R4', 'R8', 'Cn', 'Bn', 'Dn', 'N1']
        if len(buf) < 1:
            return None, ''
        else:
            typ = buf[0]
            buf = buf[1:]
            r, buf = self._get_parse_func(data_type[typ])(data_type[typ], buf)
            return r, buf

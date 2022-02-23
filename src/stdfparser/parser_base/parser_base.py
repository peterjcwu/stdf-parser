import sys
import struct
import math
import logging
import gzip
from .stdf_V4 import Rec_Dict4


class ParserBase:
    def __init__(self):
        self.data = {}
        self.Rec_Dict = Rec_Dict4
        self.Cur_Rec = None
        self.ENDIAN = '<'  # only support cpu-type == 2

    def parse(self, file_path: str):
        if file_path.endswith(".gz"):
            fd = gzip.open(file_path)
        else:
            fd = open(file_path, "rb")

        while True:
            r = self._get_header(fd)
            if r == 'EOF':  # No data in file anymore, break
                break
            else:
                slen, (typ, sub) = r  # buf length and type,sub is returned

            buf = fd.read(slen)
            assert len(buf) == slen, 'Not enough data read from %s for record %s' % (
                file_path, str(self.Rec_Dict[(typ, sub)]))
            self.process(buf)
            self.take((typ, sub))

        fd.close()

    def _set_endian(self, cpu_type):
        if cpu_type == 1:
            logging.info('Set to Big Endian Mode')
            self.ENDIAN = '>'
        elif cpu_type == 2:
            logging.info('Set to Small Endian Mode')
            self.ENDIAN = '<'
        elif cpu_type == 0:
            logging.critical('DEC PDP-11 or VAX processors, not supported!')
            sys.exit(0)

    def _get_header(self, fd):
        # STDF header is 4 bytes long
        buf = fd.read(4)
        if len(buf) == 0:
            return 'EOF'
        elif len(buf) != 4:
            logging.critical('_get_header: Incomplete STDF file.')
            sys.exit(-1)
        else:
            s_len = self.unp('H', buf[0:2])
            typ = buf[2]
            sub = buf[3]
            if (typ, sub) not in self.Rec_Dict:
                return s_len, (typ, sub)
            self.Cur_Rec = self.Rec_Dict[(typ, sub)]
            self.Cur_Rec_Name = str(self.Cur_Rec)
            return s_len, (typ, sub)

    def unp(self, fmt, buf):
        r, = struct.unpack(self.ENDIAN + fmt, buf)
        return r

    def take(self, typ_sub):
        if typ_sub not in self.Rec_Dict:
            return
        print('===========  Star of Record %s =======' % self.Rec_Dict[typ_sub].name)
        for i, j in self.Rec_Dict[typ_sub].fieldMap:
            print('< %s >  :   %s ---> %s' % (str(self.Rec_Dict[typ_sub]), str(i), str(self.data[i])))

    def process(self, buf):
        for i in self.Cur_Rec.fieldMap:
            tmp = i[1]
            parse_func = self.get_parse_func(tmp)
            self.data[i[0]], buf = parse_func(tmp, buf)

    def get_parse_func(self, fmt):
        if fmt in ['U4', 'U1', 'U2']:
            return self._get_Un
        elif fmt in ['I1', 'I2', 'I4']:
            return self._get_In
        elif fmt in ['R4', 'R8']:
            return self._get_Rn
        elif fmt == 'Cn' or (fmt.startswith('C') and (fmt[1:].isdigit())):
            return self._get_Cn
        elif fmt in ['B1', 'Bn', 'B0']:
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

    def _get_Nn(self, fmt, buf):
        """ Note: this function process two N1 type every time instead of one
        """
        #        logging.debug('In Get_Nn(): %s' % format)
        r = []
        if fmt == 'N1':
            if len(buf) < 1:
                return None, ''
            else:
                tmp = self.unp('B', buf[0])
                r.append(tmp & 0x0F)
                r.append(tmp >> 4)
                return r, buf[1:]
        else:
            logging.critical('_get_Nn: Error format: %s' % fmt)
            sys.exit(-1)

    def _get_Un(self, fmt, buf):
        # logging.debug('In Get_Un(): %s' % format)
        if fmt == 'U4':
            if len(buf) < 4:
                return None, ''
            else:
                r = self.unp('I', buf[0:4])
                return r, buf[4:]
        elif fmt == 'U2':
            if len(buf) < 2:
                return None, ''
            else:
                r = self.unp('H', buf[0:2])
                return r, buf[2:]
        elif fmt == 'U1':
            if len(buf) < 1:
                return None, ''
            else:
                r = self.unp('B', buf[0:1])
                return r, buf[1:]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    def _get_In(self, fmt, buf):
        if fmt == 'I4':
            if len(buf) < 4:
                return None, ''
            else:
                r = self.unp('i', buf[0:4])
                return r, buf[4:]
        elif fmt == 'I2':
            if len(buf) < 2:
                return None, ''
            else:
                r = self.unp('h', buf[0:2])
                return r, buf[2:]
        elif fmt == 'I1':
            if len(buf) < 2:
                return None, ''
            else:
                r = self.unp('b', buf[0:1])
                return r, buf[1:]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    def _get_Rn(self, fmt, buf):
        #        logging.debug('In Get_Rn() %s' % format)
        if fmt == 'R4':
            if len(buf) < 4:
                return None, ''
            else:
                r = self.unp('f', buf[0:4])
                return r, buf[4:]
        elif fmt == 'R8':
            if len(buf) < 8:
                return None, ''
            else:
                r = self.unp('d', buf[0:8])
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
                #                logging.debug('len(buf): %s' % str(len(buf)))
                return r, buf[1:]
        elif fmt == 'Cn':
            if len(buf) < 1:
                return None, ''
            else:
                char_cnt = buf[0]
                #                logging.debug('length of buf: %s' % str(len(buf)))
                #                logging.debug('length of byt: %s' % str(char_cnt))
                if len(buf) < (1 + char_cnt):
                    logging.critical(
                        'Cn: Not enough data in buffer: needed: %s, actual: %s' % (str(1 + char_cnt), str(len(buf))))
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

    def _get_Bn(self, fmt, buf):
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
                char_cnt = self.unp('B', bytes([buf[0]]))
                if len(buf) < (1 + char_cnt):
                    logging.critical('Bn: Not enough data in buffer: needed: %s, actual: %s' % (str(1 + char_cnt),
                                                                                                str(len(buf))))
                    sys.exit(-1)
                r = buf[1:(1 + char_cnt)]
                tmp = '0x'
                for i in r:
                    v = self.unp('B', i)
                    tmp = tmp + hexstring[v >> 4] + hexstring[v & 0x0F]
                r = tmp
                return r, buf[(1 + char_cnt):]
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    def _get_Dn(self, fmt, buf):
        if fmt == 'Dn':
            if len(buf) < 1:
                return None, ''
            else:
                dlen = self.unp('H', buf[0:2])
                buf = buf[2:]
                r = []
                dbyt = int(math.ceil(dlen / 8.0))
                assert len(buf) >= dbyt
                for i in range(dbyt):
                    tmp = self.unp('B', buf[i])
                    for j in range(8):
                        r.append((tmp >> j) & 0x01)
                return r, buf[dbyt:]

    def _get_Kx(self, fmt, buf):
        # first, parse the format to find out in which field of the record defined the length of the array
        assert fmt.startswith('K'), 'In Get_Kx(): format error: %s' % fmt
        assert len(fmt) == 4 or len(fmt) == 5
        # assume format = 'K3U4' or 'K13U4', then item_format = 'U4'
        item_format = fmt[-2:]
        # then index_cnt = 3 or 13
        index_cnt = fmt[1:-2]
        cnt = self.data[self.Cur_Rec.fieldMap[int(index_cnt)][0]]
        r = []
        func = self.get_parse_func(item_format)
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
        # logging.debug('In Get_Vn(): %s' % format)
        data_type = ['B0', 'U1', 'U2', 'U4', 'I1', 'I2', 'I4',
                     'R4', 'R8', 'Cn', 'Bn', 'Dn', 'N1']
        if len(buf) < 1:
            return None, ''
        else:
            typ = buf[0]
            buf = buf[1:]
            func = self.get_parse_func(data_type[typ])
            r, buf = func(data_type[typ], buf)
            return r, buf

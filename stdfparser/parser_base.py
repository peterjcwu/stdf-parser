import os
import sys
import struct
import math
import logging
from .stdf_V4 import Rec_Dict4, Far


class ParserBase:
    ENDIAN = '>'

    def __init__(self):
        self.data = {}
        self.The_End = False
        self.stdf_ver = 0
        self.Rec_Dict = Rec_Dict4
        self.RecName_Dict = {}
        self.Rec_Set = []
        self.Rec_Name_set = []  # list of records to ignore, higher priority over Rec_Set
        self.Cur_Rec = None
        self.Return = ''
        self.Ignore_File = False
        self.File_Name = ''  # set near the start of parse()

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

    def _set_stdf_ver(self, stdf_ver):
        assert stdf_ver in [3, 4], 'unknown stdf version %s' % str(stdf_ver)  # only version 3 or 4 is accepted
        self.stdf_ver = stdf_ver

        # only after the stdf version is known can the self.Rec_Dict be used.
        for i in self.Rec_Dict.keys():
            self.RecName_Dict[str(self.Rec_Dict[i])] = self.Rec_Dict[i]

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
            self.Cur_Rec = self.Rec_Dict[(typ, sub)]
            self.Cur_Rec_Name = str(self.Cur_Rec)
            return s_len, (typ, sub)

    def unp(self, fmt, buf):
        r, = struct.unpack(self.ENDIAN + fmt, buf)
        return r

    def _get_far(self, fd):
        buf = fd.read(6)
        # the fifth byte is CPU type.
        cpu_type = self.unp('B', buf[4])
        self._set_endian(cpu_type)
        stdf_ver = self.unp('B', buf[5])
        self._set_stdf_ver(stdf_ver)
        # the above two byte is endian type independent.
        # the unp for more than one byte data type can only
        # be called after _set_endian.
        s_len = self.unp('H', buf[0:2])
        assert s_len == 2, "FAR record length is not 2! s_len: %d" % s_len
        typ = self.unp('B', buf[2])
        sub = self.unp('B', buf[3])
        assert (typ, sub) == (0, 10), "Wrong FAR header: typ-%d, sub-%d" % (typ, sub)

    def take(self, typ_sub):
        print('===========  Star of Record %s =======' % str(self.Rec_Dict[typ_sub]))
        for i, j in self.Rec_Dict[typ_sub].fieldMap:
            print('< %s >  :   %s ---> %s' % (str(self.Rec_Dict[typ_sub]), str(i), str(self.data[i])))

    def process(self, buf):
        for i in self.Cur_Rec.fieldMap:
            tmp = i[1]
            parse_func = self.get_parse_func(tmp)
            self.data[i[0]], buf = parse_func(tmp, buf)

    def _check_rec_set(self):
        for i in self.Rec_Set:
            assert i in self.RecName_Dict.keys(), 'Unknown record: %s in Rec_Set' % i

    def parse(self, f: str):
        with open(f, "rb") as fd:
            while True:
                r = self._get_header(fd)
                if r == 'EOF':  # No data in file anymore, break
                    break
                else:
                    slen, (typ, sub) = r # buf length and type,sub is returned
                # break condition setup done!
                flag = self.Cur_Rec_Name not in self.Rec_Name_set
                # setting Rec_Set made Rec_Nset useless
                if self.Rec_Set == [] and flag:
                    # process all records except those in self.Rec_Nset ...
                    buf = fd.read(slen)
                    assert len(buf) == slen, 'Not enough data read from %s for record %s' % (f, str(self.Rec_Dict[(typ, sub)]))
                    self.process(buf)
                    # data is a dictionary with field name as its key
                    self.take((typ, sub))
                    # the take method is overwritten by its child to implement specific function
                elif self.Cur_Rec_Name in self.Rec_Set and flag:
                    # only process the records in Rec_Set
                    buf = fd.read(slen)
                    assert len(buf) == slen, 'Not enough data read from %s for record %s' % (f, str(self.Rec_Dict[(typ, sub)]))
                    self.process(buf)
                    self.take((typ, sub))
                else:
                    fd.seek(slen, os.SEEK_CUR)

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
    
    def _get_Nn(self, format, buf):
        """ Note: this function process two N1 type every time instead of one
        """
#        logging.debug('In Get_Nn(): %s' % format)
        r = []
        if format == 'N1':
            if len(buf) < 1:
                return (None, '')
            else:
                tmp = self.unp('B', buf[0])
                r.append(tmp & 0x0F)
                r.append(tmp >> 4)
                return (r, buf[1:])
        else:
            logging.critical('_get_Nn: Error format: %s' % format)
            sys.exit(-1)

    def _get_Un(self, format, buf):
        # logging.debug('In Get_Un(): %s' % format)
        if format == 'U4':
            if len(buf) < 4:
                return None, ''
            else:
                r = self.unp('I', buf[0:4])
                return r, buf[4:]
        elif format == 'U2':
            if len(buf) < 2:
                return None, ''
            else:
                r = self.unp('H', buf[0:2])
                return r, buf[2:]
        elif format == 'U1':
            if len(buf) < 1:
                return (None, '')
            else:
                r = self.unp('B', buf[0:1])
                return (r, buf[1:])
        else:
            logging.critical('Error format: %s' % format)
            sys.exit(-1)

    def _get_In(self, format, buf):
        if format == 'I4':
            if len(buf) < 4:
                return None, ''
            else:
                r = self.unp('i', buf[0:4])
                return (r, buf[4:])
        elif format == 'I2':
            if len(buf) < 2:
                return (None, '')
            else:
                r = self.unp('h', buf[0:2])
                return (r, buf[2:])
        elif format == 'I1':
            if len(buf) < 2:
                return (None, '')
            else:
                r = self.unp('b', buf[0:1])
                return (r, buf[1:])
        else:
            logging.critical('Error format: %s' % format)
            sys.exit(-1)

    def _get_Rn(self, format, buf):
#        logging.debug('In Get_Rn() %s' % format) 
        if format == 'R4':
            if len(buf) < 4:
                return (None, '')
            else:
                r = self.unp('f', buf[0:4])
                return (r, buf[4:])
        elif format == 'R8':
            if len(buf) < 8:
                return (None, '')
            else:
                r = self.unp('d', buf[0:8])
                return (r, buf[8:])
        else:
            logging.critical('Error format: %s' % format)
            sys.exit(-1)

    def _get_Cn(self, format, buf):
#        logging.debug('In Get_Cn(): %s' % format) 
        if format == 'C1':
            if len(buf) < 1:
                return (None, '')
            else:
                r = buf[0]
#                logging.debug('len(buf): %s' % str(len(buf)))
                return (r, buf[1:])
        elif format == 'Cn':
            if len(buf) < 1:
                return (None, '')
            else:
                char_cnt = buf[0]
#                logging.debug('length of buf: %s' % str(len(buf)))
#                logging.debug('length of byt: %s' % str(char_cnt))
                if len(buf) < (1 + char_cnt):
                    logging.critical('Cn: Not enough data in buffer: needed: %s, actual: %s' % (str(1+char_cnt), str(len(buf))))
                    #print str(self.Cur_Rec)+' : '+str(self.Rec_Cnt)
                    #for i,j in self.Cur_Rec.fieldMap:
                    #    if self.data.has_key(i):
                    #        print "%s : %s" % (str(i), str(self.data[i]))
                    #return (buf[1:], '')
                    # this return condition is only for Cn, and actually only stdf v3 Etsr(V3) encounters this problem.
                    # the recommended way is to for now, ignore these two records in self.Rec_Nset.
                    # sys.exit(-1)
                    return (buf[1:],buf[len(buf):])
                r = buf[1:(1+char_cnt)]
                return (r, buf[(1+char_cnt):])
        elif (format.startswith('C') and format[1:].isdigit()):
            if len(buf) < 1:
                return (None, '')
            else:
                cnt = int(format[1:])
                r = buf[0:cnt]
                return (r, buf[cnt:])
        else:
            logging.critical('Error format: %s' % format)
            sys.exit(-1)

    def _get_Bn(self, fmt, buf):
        hexstring = '0123456789ABCDEF'
        if fmt in ['B1', 'B0']:
            if len(buf) < 1:
                return None, ''
            else:
                r = buf[0]
                r = '0x'+hexstring[r>>4]+hexstring[r & 0x0F]
#                logging.debug('B1: len(buf): %s' % str(len(buf)))
                if len(buf) == 1:
                    return (r, '')
                else:
                    return (r, buf[1:])
        if fmt == 'Bn':
            if len(buf) < 1:
                return (None, '')
            else:
                char_cnt = self.unp('B', buf[0])
#                logging.debug('length of buf: %s' % str(len(buf)))
#                logging.debug('length of byt: %s' % str(char_cnt))
                if len(buf) < (1 + char_cnt):
                    logging.critical('Bn: Not enough data in buffer: needed: %s, actual: %s' % (str(1+char_cnt), str(len(buf))))
                    sys.exit(-1)
                r = buf[1:(1+char_cnt)]
                tmp = '0x'
                for i in r:
                    v = self.unp('B', i)
                    tmp = tmp+hexstring[v >> 4]+hexstring[v & 0x0F]
                r = tmp
                return (r, buf[(1+char_cnt):])
        else:
            logging.critical('Error format: %s' % fmt)
            sys.exit(-1)

    def _get_Dn(self, format, buf):
        if format == 'Dn':
            if len(buf) < 1:
                return (None, '')
            else:
                dlen = self.unp('H', buf[0:2])
                buf = buf[2:]
                r = []
                dbyt = int(math.ceil(dlen/8.0))
                assert len(buf) >= dbyt
                for i in range(dbyt):
                    tmp = self.unp('B',buf[i])
                    for j in range(8):
                        r.append((tmp>>j) & 0x01)
                return (r, buf[dbyt:])

    def _get_Kx(self, format, buf):
        # first, parse the format to find out in which field of the record defined the length of the array
        assert format.startswith('K'), 'In Get_Kx(): format error: %s' % format
        assert len(format) == 4 or len(format) == 5
        # assume format = 'K3U4' or 'K13U4', then item_format = 'U4'
        item_format = format[-2:]
        # then index_cnt = 3 or 13
        index_cnt = format[1:-2]
        cnt = self.data[self.Cur_Rec.fieldMap[int(index_cnt)][0]]
        r = []
        func = self.get_parse_func(item_format)
        if item_format == 'N1':
            cnt = int(math.ceil(cnt/2.0))
            for i in range(cnt):
                item, buf = func(item_format, buf)
                r.append(item[0])
                r.append(item[1])
            return (r, buf)
        else:
            for i in range(cnt):
                item, buf = func(item_format, buf)
                r.append(item)
            return (r, buf)

    def _get_Vn(self, format, buf):
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

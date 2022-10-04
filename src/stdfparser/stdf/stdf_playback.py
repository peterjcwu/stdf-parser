from util import unp, GenericOpen


class StdfPlayback:
    ENDIAN = '<'  # only support cpu-type == 2

    def __init__(self, stdf_file_path: str):
        self.stdf_file_path = stdf_file_path
        self.data = {}
        self.Cur_Rec = None

    def __iter__(self):
        with GenericOpen(self.stdf_file_path) as fp:
            while True:
                # header
                header = fp.read(4)
                if len(header) != 4:
                    break
                rec_len, typ, sub = unp(self.ENDIAN, 'H', header[0:2]), header[2], header[3]
                # body
                body = fp.read(rec_len)
                if len(body) != rec_len:
                    break
                yield (typ, sub), header, body


if __name__ == '__main__':
    import re
    from stdf.mir import MIR
    from stdf.dtr import DTR
    file_name = r"C:\log\w221_ey_dtr_split\sample\KW73P_OTPSite5_20220525113325.stdf.gz"
    mod_file_name = file_name.replace(".stdf.gz", "_ext.stdf")
    with open(mod_file_name, "wb") as f_out:
        for key, header, body in StdfPlayback(file_name):
            # if key == (1, 10):
            #     mir = MIR('<', header + body)
            #     # mir.set_value("TEST_COD", "cr1")
            #     # mir.set_value("JOB_NAM", "redfinch_A0_QUAL_BGA_dry")
            #     print(mir)
            #     f_out.write(mir.__repr__())
            if key == (50, 30):
                dtr = DTR('<', header + body)
                text = dtr.get_value("TEXT_DAT")
                if text == "Main.post_ioleak.py_lkgX33_pspu_low_x_x__":
                    f_out.write(header + body)
                    dtr.set_value("TEXT_DAT", "random_str without keyword, key1=val1, key2=123456789")
                    f_out.write(dtr.__repr__())
                else:
                    f_out.write(header + body)
            else:
                f_out.write(header + body)

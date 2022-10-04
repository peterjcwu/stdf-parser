import csv
import pandas as pd
import os
from typing import List, Tuple
from view.summary import Ieda

tds = r"C:\log\w235_char_wafer_map_sampling\48TD_site1_xy.csv"
xy_list = []
with open(tds, "r") as f_in:
    reader = csv.DictReader(f_in)
    for d in reader:
        x, y = int(d['x']), int(d['y'])
        for offset_x, offset_y in [(0, 0), (0, 2), (0, 4), (0, 6), (0, 8), (0, 10), (0, 12), (0, 14)]:
            xy_list.append((x + offset_x, y + offset_y))

df = pd.DataFrame()
print(len(xy_list))
print(len(set(xy_list)))

df['x'] = [t[0] for t in xy_list]
df['y'] = [t[1] for t in xy_list]


working_dir = r"C:\log\w235_char_wafer_map_sampling\ieda"
for cur_dir, dirs, file_names in os.walk(working_dir):
    for file_name in file_names:
        if not file_name.endswith(".csv"):
            continue
        ieda = Ieda(os.path.join(cur_dir, file_name))
        sb_list = [ieda.get_sb(xy) for xy in xy_list]
        df[file_name.replace(".csv", "")] = sb_list

df.to_csv(r"c:\tmp\d.csv")

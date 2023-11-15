import json
import os
import pandas as pd
from omegaconf import OmegaConf
from collections import OrderedDict
from typing import Union
from pathlib import Path

CSV_EXTENSION = ".csv"
KEY = "url"

def to_csv(df: pd.DataFrame, path: os.PathLike, time_serial: str) -> bool:
    # create directory if not exists
    directory = Path(path).parent
    if not directory.exists():
        os.makedirs(directory, exist_ok=True)

    try:
        df["detection_time"] = time_serial

        path = str(path).split(".csv")[0] + CSV_EXTENSION
        if os.path.exists(path):
            existed_df = pd.read_csv(path, index_col="idx")
            set1 = existed_df[KEY]
            set2 = df[KEY]  # new
            df = df.loc[set2[~set2.isin(set1)].index, :]

            # concat
            df = pd.concat([existed_df, df], axis=0).reset_index(drop=True)
        df.to_csv(path, index_label="idx")
    except:
        raise BaseException("csv 변환 과정에서 문제가 발생했습니다.")


def read_conf(fpath) -> Union[dict, OrderedDict]:
    fpath = Path(fpath)
    if fpath.suffix == '.yaml':
        cfgfile = OmegaConf.load(fpath)
        return OmegaConf.to_container(cfgfile, resolve=True)
    else:
        with fpath.open('rt') as f:
            return json.load(f, object_hook=OrderedDict)

def write_conf(config, fpath):
    fpath = Path(fpath)
    if fpath.suffix == '.yaml':
        OmegaConf.save(config, fpath)
    else:
        with fpath.open('wt') as f:
            json.dump(config, f, indent=4, sort_keys=False)
import os
import crawl
import argparse
import pandas as pd
from utils import to_csv
from argparse import RawTextHelpFormatter
from distutils.util import strtobool
from pathlib import Path
from parse_config import ConfigParser
from postgresql.postgre import CRUD


def run(config: ConfigParser):
    exper_name = config.exper_name
    logger = config.get_logger(exper_name)
    
    task = config['task']
    crawler = config.init_obj('crawler', crawl, config, logger)
    if task == 'search':
        for idx, query in crawler.queries.items():
            path = config.result_dir / f'query{idx}.csv'
            if path.exists():
                logger.info("query {} is already searched.")
                continue
            
            init_html = crawler.request_query(query)
            result = crawler(init_html)     # recurisive
            
            if len(result) == 0:
                message = "query {} has no results.".format(query)
                logger.info(message)
                continue
            
            result['query'] = query
            to_csv(result, path, time_serial=config.run_id)
    
    if task == 'update':
        result_dir = config.result_dir

        # load postgresql
        db = CRUD(dbname="postgres")
        do_labeling = config['do_labeling']
        if do_labeling is False:
            results = os.listdir(result_dir)
            for result in results:
                path = result_dir / result
                df = pd.read_csv(path, index_col='idx')
                
                for idx, row in df.iterrows():
                    db.insertDB(
                        table=config.exper_name,
                        columns=list(row.index),
                        values=row.values.tolist()
                    )
        else:
            names = ['google', 'instagram', 'bing', 'youtube']
            for name in names:
                urls = db.readDB(table=f"{name}", columns=["url"], condition=f"label is null")
                urls = list(map(lambda url: url[0], urls))
                
                results = crawler.labeling(urls)
                if results:
                    print("update to db...", end=' ')
                    for url, label in results:
                        db.updateDB(
                            name, columns=['label'], values=[label], condition=f"url='{url}'"
                        )
                    print("complete")
            
    return


if __name__ == "__main__":
    args = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    
    args.add_argument("--config", type=str, default="./config/youtube.yaml" ,help='config 파일의 위치를 지정합니다.')
    args.add_argument("--task", type=str, default="update", help="""
    description:
        소프트웨어가 수행할 task를 명시합니다.
        
    options:
        search: 특정 홈페이지에 검색어 사전을 사용해 검색한 후, 검색 결과를 로컬에 저장하는 Task를 수행합니다. (default)
        update: 로컬에 저장된 검색 결과들을 DB에 저장합니다. 'search' Task가 선행되어야 합니다.
    """)
    args.add_argument("--custom_time_serial", type=str, required=False, help="""
    description:
        이전 날짜에 수집된 데이터에 대한 작업을 수행할 경우 수집된 날짜를 명시합니다.
    
    example:
        python main.py --custom_time_serial 230829
        '230829'에 수집된 데이터에 대해 작업을 진행함.
    """)
    args.add_argument("--do_labeling", default=False, type=lambda x: bool(strtobool(str(x))), help="""
    description:
        DB에 있는 데이터를 labeling 할 지 여부를 결정합니다.
        
    options:
        False, false, f, n: DB에 있는 데이터를 labeling 하지 않습니다. (default)
        True, true, t, y: DB에 있는 데이터를 labeling 합니다.
    """)
    
    config = ConfigParser.from_args(args)
    run(config)
    
    
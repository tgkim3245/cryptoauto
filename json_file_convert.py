from textwrap import indent
import pyupbit
import pandas as pd
import json
import os 
from pathlib import Path
import datetime

BasePath = './datas/'

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)


def df_to_json(df, file_name, record_date = True):
    date = datetime.datetime.now().strftime('_%y%m%d_%H%M%S') if record_date else ''

    js = df.to_json(
        path_or_buf=BasePath+file_name+date+'.json',
        orient='split',
        # indent=4,
        index=True
    )
    return js

def json_to_df(file_name):
    df = pd.read_json(
        BasePath+file_name+'.json', 
        orient='split')

    return df

def dict_tickers_to_json(dict, folder_name):
    date = datetime.datetime.now().strftime('_%y%m%d_%H%M%S')
    folder_name = folder_name + date
    createFolder(BasePath+folder_name)
    for dict_key in dict:
        df_to_json(dict[dict_key], folder_name+'/'+dict_key, False)

def json_to_dict_tickers(folder_name):
    dict_tickers = {}
    for file_name in os.listdir(BasePath+folder_name):
        file_name = Path(file_name).stem #확장자 때기
        df = json_to_df(folder_name+'/'+file_name)
        dict_tickers[file_name] = df
    
    return dict_tickers

if __name__ == "__main__":
    # df = pyupbit.get_ohlcv("KRW-IQ", count=5, interval=5)
    
    # print("df",df)
    # df_to_json(df,'test')

    # rdf = json_to_df('test')
    # print('rdf',rdf)
    print(datetime.datetime.now().strftime('_%y%m%d_%H%M%S'))
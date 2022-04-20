import pandas as pd
import os
from pymongo import MongoClient
import time
import itertools
import datetime

from urllib.parse import quote_plus

db_address_port = quote_plus('data.stableprice.com')
db_port = 33310
# db_username = quote_plus('auCEGPscPRR43edF3')
# db_password = quote_plus('GF+_T9+qm+ycu2sNLm8Nrq9_qCsk')

db_username = quote_plus('iZxiIDuHD3c8MF9')
db_password = quote_plus('LDkRslTjSkKsgcE')

db_auth_db = 'admin'
indexDB_connection_string = f'mongodb://{db_username}:{db_password}@' \
                            f'{db_address_port}:{db_port}/{db_auth_db}'

db_client = MongoClient(indexDB_connection_string)  # Change the connection string of DB in db_connection.py

def update_db(source, new_df, col_name):
    one_id_df = new_df.loc[:, [col_name]]
    one_id_df.dropna(how='any', inplace=True)
    new_data = one_id_df.to_dict('dict')[col_name]
    new_data['_id'] = col_name
    to_enter_db = new_data
    to_enter_db = {(k.replace('.', '-') if isinstance(k, str) else str(k).replace('.', '-')): v
                   for (k, v) in to_enter_db.items()}
    if len(to_enter_db) > 1:
        db_client['Index_Scrapes'][source].update_one(filter={'_id': to_enter_db['_id']},
                                                      update={'$set': to_enter_db},
                                                      upsert=True)







def read_csv(csv_file):
    print(f'Reading {csv_file}')
    scrapes_df = pd.read_csv(f'reports/scrapes/{csv_file}')
    scrapes_df['unique_id'] = scrapes_df[['source', 'original_index_id']].agg('\t'.join, axis=1)
    new_df = scrapes_df[['unique_id', 'published_date', 'price']]
    new_df.rename(columns={'published_date': 'Date'}, inplace=True)
    new_df['Date'] = pd.to_datetime(new_df['Date'], errors='coerce').dt.normalize()
    new_df.dropna(how='any', inplace=True)
    new_df = new_df.pivot_table(values='price',
                                columns='unique_id',
                                index='Date')
    # Updating DB
    source = csv_file[:-4]
    # source = "IT45_piuprezzi"
    # source = 'Mercaris'
    # source = 'Leftfield'
    print(f'Updating DB with {source}')
    config_to_loop = list(itertools.product([source], [new_df], list(new_df)))
    [update_db(x[0], x[1], x[2]) for x in config_to_loop]


def main():
    # # Reading csvs (If using CSV pipeline)
    print('Reading csv files')
    csv_files = os.listdir('reports/scrapes')
    csv_files = [x for x in csv_files if x != '.DS_Store']
    for csv_file in csv_files:
        read_csv(csv_file)
    db_client.close()


if __name__ == '__main__':
    main()
    print(f'Last Update Finished: {datetime.datetime.now()}')

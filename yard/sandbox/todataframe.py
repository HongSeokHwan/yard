# -*- coding: utf-8 -*-

import MySQLdb as mdb
import csv
import MySQLdb as mdb
import pandas as pd
import pandas.io.sql as psql


ICBIT_CODE_1409 = 'BUU4'
ICBIT_CODE_1412 = 'BUZ4'
KORBIT_CODE = 'KORBIT'
BITSTAMP_CODE = 'BITSTAMP'
BTCCHINA_CODE = 'BTCCHINA'

USDKRW = 'USDKRW'
USDCNY = 'USDCNY'
KRWCNY = 'KRWCNY'


def dataframe_from_db(con, code, start_date, end_date):
    query_template = "select * from detail_quotes where code = '%s' "\
        "and dt >= '%s' and dt <= '%s'"

    with con:
        query = query_template % (code, start_date, end_date)
        df = psql.frame_query(query, con)
        df.set_index(['dt'], inplace=True)
        df.rename(columns=lambda x: '%s_%s' % (code, x), inplace=True)
        #print df.columns
        #print df.index
        #print df.columns.values
        #print df
    return df


def main():
    START_DATE = '2014-08-01'
    END_DATE = '2014-08-06'

    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    korbit_df = dataframe_from_db(con, KORBIT_CODE, START_DATE, END_DATE)

    bitstamp_df = dataframe_from_db(con, BITSTAMP_CODE, START_DATE, END_DATE)
    usdkrw_df = dataframe_from_db(con, USDKRW, START_DATE, END_DATE)

    print 'start join.'

    joined_df = korbit_df.join(bitstamp_df, how='inner')
    joined_df = joined_df.join(usdkrw_df, how='inner')
    #print joined_df.columns
    #print joined_df.index
    #print joined_df
    joined_df.to_csv('dataframe.csv')
    print 'after to csv.'


if __name__ == '__main__':
    main()

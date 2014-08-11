import MySQLdb as mdb
import pandas.io.sql as psql
import StringIO

from yard import settings


COLUMN_ALL = '*'
COLUMN_SIMPLE = 'dt, bid_price1, ask_price1'


def dataframe_from_db(con, code, column, start_date, end_date):
    query_template = "select %s from detail_quotes where code = '%s' "\
        "and dt >= '%s' and dt <= '%s' and bid_price1 > 0"

    with con:
        query = query_template % (column, code, start_date, end_date)
        df = psql.frame_query(query, con)
        df.set_index(['dt'], inplace=True)
        #df = df[df.bid_price1 > 0]
        df.rename(columns=lambda x: '%s_%s' % (code, x), inplace=True)
    return df


def to_csv(codes, start_date, end_date, outstream):
    column = COLUMN_SIMPLE

    db_info = settings.PERIODIC_QUOTE_DATABASE
    con = mdb.connect(host=db_info['host'],
                      port=db_info['port'],
                      user=db_info['user'],
                      passwd=db_info['passwd'],
                      db=db_info['database'])

    df_sum = None
    for code in codes:
        df = dataframe_from_db(con, code, column, start_date, end_date)
        if df_sum is None:
            df_sum = df
        else:
            df_sum = df_sum.join(df, how='inner')
    s = StringIO.StringIO()

    if df_sum is not None:
        df_sum.to_csv(outstream)

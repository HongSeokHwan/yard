import subprocess
from subprocess import PIPE

import MySQLdb as mdb

#from django.shortcuts import render
from django.http import HttpResponse

#from yard.apps.trading import strategy
from yard import settings
from yard.utils.tocsv import to_csv


def help(request):
    content = """
    Usage:
http://www.jiref.com/study/quotedata?codes=BITSTAMP&codes=KORBIT&codes=BTCCHINA&codes=USDKRW&codes=CNYKRW&start_date=2014-01-01&end_date=2014-12-31&column=*
codes = [
    ICBIT_CODE_1409 = 'BUU4'
    ICBIT_CODE_1412 = 'BUZ4'
    KORBIT_CODE = 'KORBIT'
    BITSTAMP_CODE = 'BITSTAMP'
    BTCCHINA_CODE = 'BTCCHINA'

    USDKRW = 'USDKRW'
    USDCNY = 'USDCNY'
    KRWCNY = 'KRWCNY'
    CNYKRW = 'CNYKRW'
]

column = [
'*',
'dt, bid_price1, bid_quantity1, ask_price1, ask_quantity1',
]
    """
    return HttpResponse('<br />'.join(content.split('\n')))


def _get_ps_result():
    p1 = subprocess.Popen(['ps', 'aux'], stdout=PIPE)
    p2 = subprocess.Popen(['grep', 'collectdetailquote'],
                          stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    process_list = p2.communicate()[0]
    return process_list


def _get_df_result():
    p = subprocess.Popen(['df', '-h'], stdout=PIPE)
    result = p.communicate()[0]
    print result
    return result


def _get_db_last_updated_date():
    db_info = settings.PERIODIC_QUOTE_DATABASE
    con = mdb.connect(host=db_info['host'],
                      port=db_info['port'],
                      user=db_info['user'],
                      passwd=db_info['passwd'],
                      db=db_info['database'])

    query = 'select dt from detail_quotes order by dt desc limit 1'
    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    return ''


def systeminfo(request):
    template = """
    1. ps -aux | grep 'collectdetailquote.py'
    %s

    2. df -h
    %s

    3. database last updated
    %s

    """

    ps = _get_ps_result()
    df = _get_df_result()
    last_updated = _get_db_last_updated_date()

    html = '<br />'.join((template % (ps, df, last_updated)).split('\n'))

    return HttpResponse(html)


def index(request):
    return systeminfo(request)
    #return help(request)


def quotedata(request):
    if request.method == 'GET':
        codes = request.GET.getlist('codes')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        column = request.GET.get('column', '')

        response = HttpResponse(content_type='text/csv')

        output = to_csv(codes, column, start_date, end_date, response)

        return response

    elif request.method == 'POST':
        return HttpResponse('Post not supported')
    return HttpResponse('Unknown request method(%s)' % request.method)

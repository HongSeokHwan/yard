#from django.shortcuts import render
from django.http import HttpResponse

#from yard.apps.trading import strategy
from yard.utils.tocsv import to_csv


def index(request):
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

#from django.shortcuts import render
from django.http import HttpResponse

#from yard.apps.trading import strategy
from yard.utils.tocsv import to_csv


def index(request):
    content = """
    Usage:
http://14.63.217.41:8000/study/?codes=&codes=&start_date=2014-01-01&end_date=2014-12-31
codes = [
    ICBIT_CODE_1409 = 'BUU4'
    ICBIT_CODE_1412 = 'BUZ4'
    KORBIT_CODE = 'KORBIT'
    BITSTAMP_CODE = 'BITSTAMP'
    BTCCHINA_CODE = 'BTCCHINA'

    USDKRW = 'USDKRW'
    USDCNY = 'USDCNY'
    KRWCNY = 'KRWCNY'
]
    """
    return HttpResponse('<br />'.join(content.split('\n')))


def quotedata(request):
    if request.method == 'GET':
        codes = request.GET.getlist('codes')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        response = HttpResponse(content_type='text/csv')

        output = to_csv(codes, start_date, end_date, response)

        return response

    elif request.method == 'POST':
        return HttpResponse('Post not supported')
    return HttpResponse('Unknown request method(%s)' % request.method)

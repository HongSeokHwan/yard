#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import urllib2
import MySQLdb as mdb
import xml.etree.ElementTree as ET


ICBIT_URL_TEMPLATE = 'https://api.icbit.se/api/orders/book?ticker=%s'
KORBIT_URL = 'https://api.korbit.co.kr/v1/orderbook'
BITSTAMP_URL = 'https://www.bitstamp.net/api/order_book/'
CURRENCY_URL_TEMPLATE = 'http://www.webservicex.net/CurrencyConvertor.asmx/' \
                            'ConversionRate?FromCurrency=%s&ToCurrency=%s'

def get_quote(url):
    req = urllib2.Request(url)
    req.add_unredirected_header('User-Agent',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, ' \
            'like Gecko) Chrome/26.0.1410.64 Safari/537.31')
    source = urllib2.urlopen(req).read()
    return source

def get_currency(from_currency, to_currency):
    url = CURRENCY_URL_TEMPLATE % (from_currency, to_currency)
    return get_quote(url)

def parse_currency_value(content):
    root = ET.fromstring(content)
    return root.text


def insert_into_db(con, datetime, code, value):
    with con:
        cur = con.cursor()
        query = "INSERT INTO quote(dt, code, value) VALUES ('%s', '%s', '%s')"\
                % (datetime, code, value)
        cur.execute(query)

def main():
    ICBIT_CODE_1409 = 'BUU4'
    ICBIT_CODE_1412 = 'BUZ4'
    KORBIT_CODE = 'KORBIT'
    BITSTAMP_CODE = 'BITSTAMP'
    USDKRW = 'USDKRW'

    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard');
    while True:
        print 'start get quote'

        icbit_quote_1409 = get_quote(ICBIT_URL_TEMPLATE % ICBIT_CODE_1409)
        icbit_quote_1412 = get_quote(ICBIT_URL_TEMPLATE % ICBIT_CODE_1412)
        korbit_quote = get_quote(KORBIT_URL)
        bitstamp_quote = get_quote(BITSTAMP_URL)
        usdkrw_content = get_currency('USD', 'KRW')
        usdkrw_value = parse_currency_value(usdkrw_content)

        now = datetime.datetime.now()
        dt = time.strftime('%Y-%m-%d %H:%M:%S')

        insert_into_db(con, dt, ICBIT_CODE_1409, icbit_quote_1409)
        insert_into_db(con, dt, ICBIT_CODE_1412, icbit_quote_1412)
        insert_into_db(con, dt, KORBIT_CODE, korbit_quote)
        insert_into_db(con, dt, BITSTAMP_CODE, bitstamp_quote)
        insert_into_db(con, dt, USDKRW, usdkrw_value)

        print 'end get quote and insert into db.', now
        time.sleep(30)

if __name__ == '__main__':
    main()


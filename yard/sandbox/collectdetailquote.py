#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import datetime
import urllib2
import MySQLdb as mdb
import xml.etree.ElementTree as ET


ICBIT_CODE_1409 = 'BUU4'
ICBIT_CODE_1412 = 'BUZ4'
KORBIT_CODE = 'KORBIT'
BITSTAMP_CODE = 'BITSTAMP'
BTCCHINA_CODE = 'BTCCHINA'

USDKRW = 'USDKRW'
USDCNY = 'USDCNY'
KRWCNY = 'KRWCNY'
CNYKRW = 'CNYKRW'


ICBIT_URL_TEMPLATE = 'https://api.icbit.se/api/orders/book?ticker=%s'
KORBIT_URL = 'https://api.korbit.co.kr/v1/orderbook'
BITSTAMP_URL = 'https://www.bitstamp.net/api/order_book/'
BTCCHINA_URL = 'https://data.btcchina.com/data/ticker?market=btccny'
CURRENCY_URL_TEMPLATE = 'http://www.webservicex.net/CurrencyConvertor.asmx/' \
    'ConversionRate?FromCurrency=%s&ToCurrency=%s'


class Quote:
    query_template = """
    insert into detail_quotes (
    dt, code,

    bid_price1, bid_price2, bid_price3, bid_price4, bid_price5,
    bid_price6, bid_price7, bid_price8, bid_price9, bid_price10,

    ask_price1, ask_price2, ask_price3, ask_price4, ask_price5,
    ask_price6, ask_price7, ask_price8, ask_price9, ask_price10,

    bid_quantity1, bid_quantity2, bid_quantity3, bid_quantity4, bid_quantity5,
    bid_quantity6, bid_quantity7, bid_quantity8, bid_quantity9, bid_quantity10,

    ask_quantity1, ask_quantity2, ask_quantity3, ask_quantity4, ask_quantity5,
    ask_quantity6, ask_quantity7, ask_quantity8, ask_quantity9, ask_quantity10)

    VALUES ('%s', '%s', %s %s %s %s)"""

    ten_array_template_with_comma = """
    %f, %f, %f, %f, %f,
    %f, %f, %f, %f, %f,"""

    ten_array_template_without_comma = """
    %f, %f, %f, %f, %f,
    %f, %f, %f, %f, %f"""

    def __init__(self):
        self.code = ''
        self.bid_prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ask_prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.bid_quantities = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ask_quantities = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def btcchina_to_quote(self, raw_quote):
        self.code = BTCCHINA_CODE
        try:
            j = json.loads(raw_quote)
            data = j['ticker']
            self.bid_prices[0] = float(data['buy'])
            self.ask_prices[0] = float(data['sell'])

            return True

        except Exception, e:
            print str(e)
            return False

    def bitstamp_to_quote(self, bitstamp_quote):
        self.code = BITSTAMP_CODE
        try:
            j = json.loads(bitstamp_quote)
            i = 0
            while True:
                if i >= 10:
                    break

                self.bid_prices[i] = float(j['bids'][i][0])
                self.bid_quantities[i] = float(j['bids'][i][1])
                self.ask_prices[i] = float(j['asks'][i][0])
                self.ask_quantities[i] = float(j['asks'][i][1])

                i += 1
            return True

        except Exception, e:
            print str(e)
            return False

    def currency_to_quote(self, code, quote):
        self.code = code
        self.bid_prices[0] = quote
        self.ask_prices[0] = quote

    def korbit_to_quote(self, korbit_quote):
        self.code = KORBIT_CODE
        try:
            j = json.loads(korbit_quote)
            i = 0
            while True:
                if i >= 10:
                    break

                self.bid_prices[i] = float(j['bids'][i][0])
                self.bid_quantities[i] = float(j['bids'][i][1])
                self.ask_prices[i] = float(j['asks'][i][0])
                self.ask_quantities[i] = float(j['asks'][i][1])

                i += 1
            return True

        except Exception, e:
            print str(e)
            return False

    def icbit_to_quote(self, code, icbit_quote):
        self.code = code
        try:
            j = json.loads(icbit_quote)

            i = 0
            while True:
                if i >= 10:
                    break

                self.bid_prices[i] = float(j['buy'][i]['p'])
                self.bid_quantities[i] = float(j['buy'][i]['q'])
                self.ask_prices[i] = float(j['sell'][i]['p'])
                self.ask_quantities[i] = float(j['sell'][i]['q'])

                i += 1
            return True

        except Exception, e:
            print str(e)
            return False

    def create_query(self, dt):
        bid_price_str = Quote.ten_array_template_with_comma % (
                self.bid_prices[0], self.bid_prices[1],
                self.bid_prices[2], self.bid_prices[3],
                self.bid_prices[4], self.bid_prices[5],
                self.bid_prices[6], self.bid_prices[7],
                self.bid_prices[8], self.bid_prices[9])

        ask_price_str = Quote.ten_array_template_with_comma % (
                self.ask_prices[0], self.ask_prices[1],
                self.ask_prices[2], self.ask_prices[3],
                self.ask_prices[4], self.ask_prices[5],
                self.ask_prices[6], self.ask_prices[7],
                self.ask_prices[8], self.ask_prices[9])

        bid_quantity_str = Quote.ten_array_template_with_comma % (
                self.bid_quantities[0], self.bid_quantities[1],
                self.bid_quantities[2], self.bid_quantities[3],
                self.bid_quantities[4], self.bid_quantities[5],
                self.bid_quantities[6], self.bid_quantities[7],
                self.bid_quantities[8], self.bid_quantities[9])

        ask_quantity_str = Quote.ten_array_template_without_comma % (
                self.ask_quantities[0], self.ask_quantities[1],
                self.ask_quantities[2], self.ask_quantities[3],
                self.ask_quantities[4], self.ask_quantities[5],
                self.ask_quantities[6], self.ask_quantities[7],
                self.ask_quantities[8], self.ask_quantities[9])

        query = Quote.query_template % (
                dt, self.code,
                bid_price_str,
                ask_price_str,
                bid_quantity_str,
                ask_quantity_str)

        #print 'query', query
        return query

    def to_database(self, con, dt):
        with con:
            cur = con.cursor()
            query = self.create_query(dt)
            cur.execute(query)


def get_quote(url):
    req = urllib2.Request(url)
    req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; '
                                'WOW64) AppleWebKit/537.31 (KHTML, '
                                'like Gecko) Chrome/26.0.1410.64 Safari/537.31')
    source = urllib2.urlopen(req).read()
    return source


def get_currency(from_currency, to_currency):
    url = CURRENCY_URL_TEMPLATE % (from_currency, to_currency)
    return get_quote(url)


def parse_currency_value(content):
    root = ET.fromstring(content)
    return root.text


def _main(con):
    print 'start collectdetailquote.'

    # futures data
    raw_icbit_quote_1409 = get_quote(ICBIT_URL_TEMPLATE % ICBIT_CODE_1409)
    icbit_quote_1409 = Quote()
    icbit_quote_1409.icbit_to_quote(ICBIT_CODE_1409, raw_icbit_quote_1409)

    raw_icbit_quote_1412 = get_quote(ICBIT_URL_TEMPLATE % ICBIT_CODE_1412)
    icbit_quote_1412 = Quote()
    icbit_quote_1412.icbit_to_quote(ICBIT_CODE_1412, raw_icbit_quote_1412)

    # btc data
    raw_korbit_quote = get_quote(KORBIT_URL)
    korbit_quote = Quote()
    korbit_quote.korbit_to_quote(raw_korbit_quote)

    raw_bitstamp_quote = get_quote(BITSTAMP_URL)
    bitstamp_quote = Quote()
    bitstamp_quote.bitstamp_to_quote(raw_bitstamp_quote)

    raw_btcchina_quote = get_quote(BTCCHINA_URL)
    btcchina_quote = Quote()
    btcchina_quote.btcchina_to_quote(raw_btcchina_quote)

    # currency data
    usdkrw_content = get_currency('USD', 'KRW')
    usdkrw_value = float(parse_currency_value(usdkrw_content))
    usdkrw_quote = Quote()
    usdkrw_quote.currency_to_quote(USDKRW, usdkrw_value)

    usdcny_content = get_currency('USD', 'CNY')
    usdcny_value = float(parse_currency_value(usdcny_content))
    usdcny_quote = Quote()
    usdcny_quote.currency_to_quote(USDCNY, usdcny_value)

    krwcny_content = get_currency('KRW', 'CNY')
    krwcny_value = float(parse_currency_value(krwcny_content))
    krwcny_quote = Quote()
    krwcny_quote.currency_to_quote(KRWCNY, krwcny_value)

    cnykrw_content = get_currency('CNY', 'KRW')
    cnykrw_value = float(parse_currency_value(cnykrw_content))
    cnykrw_quote = Quote()
    cnykrw_quote.currency_to_quote(CNYKRW, cnykrw_value)

    # date
    now = datetime.datetime.now()
    dt = time.strftime('%Y-%m-%d %H:%M:%S')

    # to database
    icbit_quote_1409.to_database(con, dt)
    icbit_quote_1412.to_database(con, dt)
    korbit_quote.to_database(con, dt)
    bitstamp_quote.to_database(con, dt)
    btcchina_quote.to_database(con, dt)
    usdkrw_quote.to_database(con, dt)
    usdcny_quote.to_database(con, dt)
    krwcny_quote.to_database(con, dt)
    cnykrw_quote.to_database(con, dt)

    print 'end get quote and insert into db.', now
    time.sleep(30)


def main():
    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    while True:
        try:
            _main(con)
        except:
            try:
                con.close()
            except:
                pass
            con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')


if __name__ == '__main__':
    main()

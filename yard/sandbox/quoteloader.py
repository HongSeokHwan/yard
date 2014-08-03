#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import json

ICBIT_CODE_1412 = 'BUZ4'
ICBIT_CODE_1409 = 'BUU4'


class UsdKrxConverter:
    def __init__(self):
        self.data = []

    def set_data(self, rows):
        for row in rows:
            self.data.append(float(row['value']))


class SimpleQuote:
    def __init__(self):
        self.bid_price1 = 0.0
        self.ask_price1 = 0.0
        self.bid_quantityi1 = 0.0
        self.ask_quantity1 = 0.0
        self.spread = 0.0
        self.spread_rate = 0.0
        self.mid_price = 0.0

    def parse_icbit(self, raw_string):
        try:
            j = json.loads(raw_string)
            # print j
            # print j['asks'][1][0]
            # print j['asks'][0][0]
            # print j['bids'][0][0]
            # print j['bids'][1][0]

            self.bid_price1 = float(j['buy'][0]['p'])
            self.bid_quantity1 = float(j['buy'][0]['q'])

            self.ask_price1 = float(j['sell'][0]['p'])
            self.ask_quantity1 = float(j['sell'][0]['q'])

            self.spread = self.ask_price1 - self.bid_price1
            self.spread_rate = (self.ask_price1 / self.bid_price1) - 1
            self.mid_price = (self.ask_price1 + self.bid_price1) / 2
            return True
        except Exception, e:
            print str(e)
            return False

    def parse_korbit(self, raw_string):
        try:
            j = json.loads(raw_string)
            # print j['asks'][1][0]
            # print j['asks'][0][0]
            # print j['bids'][0][0]
            # print j['bids'][1][0]

            self.bid_price1 = float(j['bids'][0][0])
            self.bid_quantity1 = float(j['bids'][0][1])

            self.ask_price1 = float(j['asks'][0][0])
            self.ask_quantity1 = float(j['asks'][0][1])

            self.spread = self.ask_price1 - self.bid_price1
            self.spread_rate = (self.ask_price1 / self.bid_price1) - 1
            self.mid_price = (self.ask_price1 + self.bid_price1) / 2
            return True
        except Exception, e:
            print str(e)
            return False

    def parse_bitstamp(self, raw_string):
        try:
            j = json.loads(raw_string)
            self.ask_price1 = float(j['asks'][1][0])
            self.ask_quantity1 = float(j['asks'][1][1])

            self.bid_price1 = float(j['bids'][1][0])
            self.bid_quantity1 = float(j['bids'][1][1])

            self.spread = (self.ask_price1 / self.bid_price1) - 1
            self.mid_price = (self.ask_price1 + self.bid_price1) / 2

            # print self.mid_price, self.spread

            return True
        except Exception, e:
            print str(e)
            return False


def get_usdkrx_data(start_date, end_date):
    CODE = 'USDKRW'
    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    query_template = "select * from quote where code = '%s' "\
        "and dt >= '%s' and dt <= '%s'"

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query_template % (CODE, start_date, end_date))
        rows = cur.fetchall()
        converter = UsdKrxConverter()
        converter.set_data(rows)
        return converter


def get_korbit_data(start_date, end_date):
    CODE = 'KORBIT'
    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    query_template = "select * from quote where code = '%s' "\
        "and dt >= '%s' and dt <= '%s'"

    quotes = []

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query_template % (CODE, start_date, end_date))
        rows = cur.fetchall()
        for row in rows:
            quote = SimpleQuote()
            success = quote.parse_korbit(row['value'])
            if success:
                quotes.append(quote)
            else:
                return None
    return quotes


def get_bitstamp_data(start_date, end_date):
    CODE = 'BITSTAMP'
    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    query_template = "select * from quote where code = '%s' "\
        "and dt >= '%s' and dt <= '%s'"

    quotes = []

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query_template % (CODE, start_date, end_date))
        rows = cur.fetchall()
        for row in rows:
            quote = SimpleQuote()
            success = quote.parse_bitstamp(row['value'])
            if success:
                quotes.append(quote)
            else:
                return None
    return quotes


def get_icbit_data(code, start_date, end_date):
    CODE = code
    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    query_template = "select * from quote where code = '%s' "\
        "and dt >= '%s' and dt <= '%s'"

    quotes = []

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query_template % (CODE, start_date, end_date))
        rows = cur.fetchall()
        for row in rows:
            quote = SimpleQuote()
            success = quote.parse_icbit(row['value'])
            if success:
                quotes.append(quote)
            else:
                return None
    return quotes


def get_mid_prices(simple_quotes):
    quotes = []
    for simple_quote in simple_quotes:
        quotes.append(simple_quote.mid_price)
    return quotes


def get_spreads(simple_quotes):
    quotes = []
    for simple_quote in simple_quotes:
        quotes.append(simple_quote.spread)
    return quotes


def get_krxbase_data(usdbase_data, currency):
    krxbase_data = []
    i = 0
    for data in usdbase_data:
        krxbase_data.append(data * currency[i])
        i += 1
    return krxbase_data


def get_diffs(a, b):
    diffs = []
    i = 0
    for row in a:
        diff = row - b[i]
        diffs.append(diff)
    return diffs


def get_rate_percents(a, b):
    rets = []
    i = 0
    for row in a:
        ret = row * 100 / b[i]
        rets.append(ret)
    return rets


def get_rates(a, b):
    rets = []
    i = 0
    for row in a:
        ret = row / b[i]
        rets.append(ret)
    return rets


def main():
    start = '2014-08-01'
    end = '2014-08-31'
    usdkrx_converter = get_usdkrx_data(start, end)

    bitstamp_quotes = get_bitstamp_data(start, end)
    bitstamp_mids = get_mid_prices(bitstamp_quotes)
    bitstamp_krxbase_mids = get_krxbase_data(bitstamp_mids,
                                             usdkrx_converter.data)

    icbit12_quotes = get_icbit_data(ICBIT_CODE_1412, start, end)
    icbit12_mids = get_mid_prices(icbit12_quotes)
    icbit12_krxbase_mids = get_krxbase_data(icbit12_mids,
                                            usdkrx_converter.data)

    icbit09_quotes = get_icbit_data(ICBIT_CODE_1409, start, end)
    icbit09_mids = get_mid_prices(icbit09_quotes)
    icbit09_krxbase_mids = get_krxbase_data(icbit09_mids,
                                            usdkrx_converter.data)

    korbit_quotes = get_korbit_data(start, end)
    korbit_mids = get_mid_prices(korbit_quotes)
    korbit_spreads = get_spreads(korbit_quotes)

    rates = get_rates(icbit12_krxbase_mids, korbit_mids)
    #rates = get_rates(icbit12_krxbase_mids, icbit09_krxbase_mids)

    #print rates

    myfile = open('rates.csv', 'w')
    with open('rates.csv', 'w') as fd:
        for row in rates:
            fd.write(str(row))
            fd.write('\n')

    #diffs = get_diffs(bitstamp_krxbase_mids, korbit_mids)
    #rate_percents = get_rate_percents(diffs, korbit_mids)
    #rates = get_rates(diffs, korbit_spreads)

    #print korbit_spreads
    #print diffs
    #print korbit_spreads
    #print rates

if __name__ == '__main__':
    main()

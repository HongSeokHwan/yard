#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'root', 'baadf00d', 'yard');

with con:
    
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS detail_quotes")
    cur.execute("""
create table detail_quotes (
    dt datetime,
    code varchar(256),

    bid_price1 FLOAT,
    bid_price2 FLOAT,
    bid_price3 FLOAT,
    bid_price4 FLOAT,
    bid_price5 FLOAT,
    bid_price6 FLOAT,
    bid_price7 FLOAT,
    bid_price8 FLOAT,
    bid_price9 FLOAT,
    bid_price10 FLOAT,

    ask_price1 FLOAT,
    ask_price2 FLOAT,
    ask_price3 FLOAT,
    ask_price4 FLOAT,
    ask_price5 FLOAT,
    ask_price6 FLOAT,
    ask_price7 FLOAT,
    ask_price8 FLOAT,
    ask_price9 FLOAT,
    ask_price10 FLOAT,

    bid_quantity1 FLOAT,
    bid_quantity2 FLOAT,
    bid_quantity3 FLOAT,
    bid_quantity4 FLOAT,
    bid_quantity5 FLOAT,
    bid_quantity6 FLOAT,
    bid_quantity7 FLOAT,
    bid_quantity8 FLOAT,
    bid_quantity9 FLOAT,
    bid_quantity10 FLOAT,

    ask_quantity1 FLOAT,
    ask_quantity2 FLOAT,
    ask_quantity3 FLOAT,
    ask_quantity4 FLOAT,
    ask_quantity5 FLOAT,
    ask_quantity6 FLOAT,
    ask_quantity7 FLOAT,
    ask_quantity8 FLOAT,
    ask_quantity9 FLOAT,
    ask_quantity10 FLOAT,
    INDEX detail_quotes_default_index (dt, code)
    )
""")


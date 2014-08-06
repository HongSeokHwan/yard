#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import csv


def main():
    con = mdb.connect('localhost', 'root', 'baadf00d', 'yard')
    query = 'select * from detail_quotes'
    f = open('detail_quotes.csv', 'w')
    writer = csv.writer(f)
    with con:
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        writer.writerows(rows)
    f.close()


if __name__ == '__main__':
    main()

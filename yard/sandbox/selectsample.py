#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect(host='14.63.217.41',
                  port=8088,
                  user='root',
                  passwd='baadf00d',
                  db='yard')

with con:
    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT * FROM Writers")

    rows = cur.fetchall()

    for row in rows:
        print row["Id"], row["Name"]


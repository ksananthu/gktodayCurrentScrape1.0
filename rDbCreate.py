import sqlite3

conn = sqlite3.connect('rGktoday.db')
c = conn.cursor()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS GkData(id TEXT, date TEXT, title TEXT, html TEXT, content TEXT)")


# def data_entry():
   # c.execute("INSERT INTO stuffToPlot VALUES(1452549219,'2016-01-11 13:53:39','Python',6)")

    # conn.commit()
    # c.close()
    # conn.close()

create_table()
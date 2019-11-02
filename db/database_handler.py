db_con = None
query = None


def set_db(db_name, database, host=None, username=None, password=None):
    global db_con, query
    db_name = db_name.lower()
    if db_name == "sqlite3" or db_name == "sqlite":
        import sqlite3
        db_con = sqlite3.connect(database+".db", check_same_thread=False)
        query = db_con.cursor()
    elif db_name == "mysql":
        import pymysql
        if host is not None and username is not None and password is not None:
            db_con = pymysql.connect(host, username, password, database)


def make_query(args):
    if len(args) > 1:
        resp = query.execute(args[0], args[1:])
    else:
        resp = query.execute(args[0])
    if resp is not None:
        return resp

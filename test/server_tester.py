import pywebserver, os

#pywebserver.start_server("192.168.1.14")
pywebserver.start_server("172.16.8.7")
#pywebserver.set_data_read_limit(1024)

pywebserver.match_url(
    ("^/$", "index"),
    ("^/list", "/list"),
    ("^/login", "$login")
)

pywebserver.match_url("list",
    ("^/$","list_home"),
    ("^/item$", "item")
)

os.chdir("test")
pywebserver.set_database("sqlite3", "test_proj")

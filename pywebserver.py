from core import request, server
from db import database_handler
import threading


def start_server(host="127.0.0.1", port=0, is_secure=False, family=server.AF_INET, type=server.SOCK_STREAM, ip_type=None, socket_type=None, backlog=5):
    if ip_type is None:
        ip_type = family
    if socket_type is None:
        socket_type = type
    server.create_socket(ip_type, socket_type)
    server.backlog = backlog
    if not port:
        port = 443 if is_secure else 80
    server.bind(host, port)
    threading.Thread(target=server.start).start()


def match_url(*args):
    if type(args[0]) == str:
        request.paths[args[0]] = args[1:]
    elif type(args[0]) == tuple:
        request.paths["/"] = args


set_database = database_handler.set_db
redirect = request.redirect
set_data_read_limit = server.set_read_limit
make_query = database_handler.make_query

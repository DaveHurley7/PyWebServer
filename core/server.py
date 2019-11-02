import socket
from core import request

IPV4 = AF_INET = socket.AF_INET
IPV6 = AF_INET6 = socket.AF_INET6

TCP_IP = SOCK_STREAM = socket.SOCK_STREAM
UDP = SOCK_DGRAM = socket.SOCK_DGRAM

sk = None
backlog = 5
data_limit = 1024
byte_sizes = ["K", "M", "G"]


def create_socket(family, sk_type):
    global sk
    sk = socket.socket(family, sk_type)


def bind(host, port):
    global sk
    sk.bind((host, port))
    print("Server created at:", host+":"+str(port))


def start():
    sk.listen(backlog)
    while True:
        conn, addr = sk.accept()
        load_req = conn.recv(data_limit)
        read_limit = 3
        while b'\r\n\r\n' not in load_req and read_limit > 0:
            load_req += conn.recv(data_limit)
            read_limit -= 1
        if b'\r\n\r\n' not in load_req and read_limit == 0:
            res = "HTTP/1.1 400 Bad Request".encode()
            conn.send(res)
            conn.close()
            continue
        print(load_req.decode(errors="None"))
        req_div = load_req.index(b'\r\n\r\n')
        header_info = load_req[:req_div].decode().split("\r\n")
        data_bounds = [info[info.index("boundary")+9:] for info in header_info if "boundary" in info]
        if data_bounds:
            data_bounds = b'--'+data_bounds[0].encode()
        form_data = None
        if data_bounds:
            form_data = load_req[req_div+4:]
            while not form_data.endswith(data_bounds+b'--\r\n'):
                form_data += conn.recv(data_limit)
        if header_info[0] != "":
            req_info = header_info[0].split(" ")
            req = {"method": req_info[0], "path": req_info[1],"_path_index":0}
            req["params"] = None
            if form_data is not None:
                req["params"], req["files"] = request.extract_params_from_request("multipart", form_data,data_bounds)
            else:
                if req["method"].lower() == "post":
                    data_length = int([info[16:] for info in header_info if "Content-Type" in info][0])
                    data = load_req[req_div+4:].decode()
                    while len(data) < data_length:
                        data += conn.recv(data_limit)
                    req["params"] = request.extract_params_from_request(req["method"].lower(), data)
                elif req["method"].lower() == "get":
                    req["params"] = request.extract_params_from_request(req["method"].lower(), req["path"])
            res = request.process(req)
        else:
            res = "HTTP/1.1 400 Bad Request".encode()
        conn.send(res)
        conn.close()


def set_read_limit(limit="1024"):
    global data_limit
    if type(limit) == str:
        if limit[-1] in byte_sizes:
            value = int(limit[:-1])
            size_index = byte_sizes[limit[-1]]+1
            data_limit = value*(1024**size_index)
        else:
            data_limit = int(limit)
    elif type(limit) == int:
        data_limit = limit



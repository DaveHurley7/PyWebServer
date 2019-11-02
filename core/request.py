import re
import os
from importlib import import_module
from core import page

paths = {}
media_dir = "media/"

STAT_OK = "HTTP/1.1 200 OK\r\n"
STAT_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"


def recur_path(path_dir, request):
    if request["path"] == "/favicon.ico":
        try:
            favicon = open("resources/favicon.ico")
        except FileNotFoundError:
            favicon = open(os.path.dirname(__file__)+"/favicon.png", "rb")
        return favicon.read()
    elif re.match("^/resources", request["path"]):
        return open(request["path"][1:], "rb").read()
    for path in paths[path_dir]:
        if re.match(path[0], request["path"][request["_path_index"]:]):
            if path[1][0] == "/":
                request["_path_index"] = request["path"].index("/",request["_path_index"]+1)
                return recur_path(path[1][1:], request)
            elif path[1][0] == "$":
                method_call = getattr(import_module(path[1][1:]), request["method"].lower())
                return method_call(request["params"]) if request["params"] else method_call()
            else:
                status, response = page.render(path[1])
                if status == "ERROR":
                    return STAT_NOT_FOUND+"\r\n"+response
                return STAT_OK+"\r\n"+response
    return STAT_NOT_FOUND


def process(req):
    response = recur_path("/", req)
    if type(response) == str:
        response = response.encode()
    return response


def extract_params_from_request(method, params, data_bounds=None):
    kvp_list = {}
    files = {}
    if method == "multipart":
        params = params.split(data_bounds+b'\r\n')[1:]
        params[-1] = params[-1].split(data_bounds+b'--\r\n')[0]
        for param in params:
            f_qt = param.index(b'"')+1  #Gets first pair of quotes which contain key
            f_cqt = param.index(b'"', f_qt)
            key = param[f_qt:f_cqt]
            file_name = None
            file_type = None
            if param[f_cqt+1:f_cqt+2] == b';':   #Gets second pair of quotes which for files contain their name
                n_qt = param.index(b'"', f_cqt+1) + 1
                n_cqt = param.index(b'"', n_qt)
                file_name = param[n_qt:n_cqt]
                type_div = param.index(b':', n_cqt)+2
                n_nl = param.index(b'\r\n', type_div)
                file_type = param[type_div:n_nl]
                value_start = n_nl+4
            else:
                value_start = f_cqt+5
            value = param[value_start:-2]
            key = key.decode()
            if file_name is not None and file_type is not None:
                file_name = file_name.decode()
                file_type = file_type.decode()
                if not os.path.exists(media_dir):
                    os.mkdir(media_dir[:-1])
                f_create = open(media_dir+file_name, "wb")
                f_create.write(value)
                f_create.close()
                name_index = file_name.index(".")
                name = file_name[:name_index]
                files[key] = {"name": name, "filename": file_name, "type": file_type, "path": "temp_dir/"+file_name,"size":value}
            else:
                value = value.decode()
                if key in kvp_list.keys():
                    if type(kvp_list[key]) == str:
                        kvp_list[key] = [kvp_list[key], value]
                    else:
                        kvp_list[key].append(value)
                else:
                    kvp_list[key] = value

    else:
        if method == "get":
            param_div = params.find("?") + 1
            if not param_div:
                return
            params = params[param_div:]
        if params == "":
            return
        print(params)
        params = params.split("&")
        for param in params:
            param = param.split("=")
            if param[0][-6:] == "%5B%5D":
                param[0] = param[0][:-6]
            if param[0] in kvp_list.keys():
                if type(kvp_list[param[0]]) == str:
                    kvp_list[param[0]] = [kvp_list[param[0]], param[1]]
                else:
                    kvp_list[param[0]].append(param[1])
            else:
                kvp_list[param[0]] = param[1]
    if files:
        return kvp_list, files
    else:
        return kvp_list


def redirect(template, data=None):
    return page.render(template, data)

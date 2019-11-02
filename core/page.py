import re
import sys


class TemplateRenderError(Exception):
    pass


class NoTemplateError(Exception):
    pass


class IncompleteCommentError(TemplateRenderError):
    pass


class IncompleteScriptTagError(TemplateRenderError):
    pass


reg_exps = {"startfor": re.compile("{%[ \t]*for"),
            "endfor": re.compile("{%[ \t]*endfor[ \t]*%}"),
            "startif": re.compile("{%[ \t]*if"),
            "endif": re.compile("{%[ \t]*endif[ \t]*%}"),
            "scriptstart": re.compile("{%[ \t]*(for|if)"),
            "un_newl": re.compile("\n[ \t]*$")
            }


def render(template, data=None):
    page_content = None
    try:
        file = open("templates/"+template+".html", "r")
        page_content = file.read()
        file.close()
        page_content = process(page_content, data)
        return "SUCCESS", page_content
    except FileNotFoundError:
        print("Template not found", file=sys.stderr)
        return "ERROR", page_content
    except TemplateRenderError as tre:
        print(tre, file=sys.stderr)
        return "ERROR", page_content


def process(content,data):
    content = remove_comments(content)
    if data is not None:
        page_content = render_data(content, data)
    # page_content = render_context(content)
    return content


def remove_comments(content):
    if "{#" in content:
        scmt_pos = content.find("{#")
        while scmt_pos > -1:
            ecmt_pos = content.find("#}")
            if ecmt_pos == -1:
                raise IncompleteCommentError("Server-side comment was not closed on line")
            ecmt_pos += 2
            content = content[:scmt_pos] + content[ecmt_pos:]
            content = adjust_line(content, scmt_pos)
            scmt_pos = content.find("{#")
    return content


def adjust_line(content, curr_pos):
    rm_newl = reg_exps["un_newl"].search(content, endpos=curr_pos)
    if rm_newl is not None:
        rm_newl = rm_newl.start()
        content = content[:rm_newl] + content[curr_pos:]
    return content

# def render_context(content):
#
#     return content


def render_data(content, data):
    #print(content)
    stag_spos = reg_exps["scriptstart"].search(content)
    if stag_spos is None:
        return content
    stag_spos = stag_spos.start()
    while stag_spos > -1:
        stag_epos = content.find("%}",stag_spos)
        if stag_epos == -1:
            raise IncompleteScriptTagError("A server-side tag wasn't closed")
        script = content[stag_spos+2:stag_epos].strip().split()
        if script[0] == "for":
            etag_spos = reg_exps["endfor"].search(content, stag_epos)
            if etag_spos is None:
                raise IncompleteScriptTagError("A server-side script wasn't closed")
            etag_spos = etag_spos.start()
            etag_epos = content.find("%}", etag_spos)
            if etag_epos == -1:
                raise IncompleteScriptTagError("A server-side tag wasn't closed")
            sfor_cnt = len(reg_exps["startfor"].findall(content, stag_epos, etag_spos))
            efor_cnt = len(reg_exps["endfor"].findall(content, stag_epos, etag_spos))
            while sfor_cnt != efor_cnt:
                etag_epos += 2
                etag_spos = reg_exps["endfor"].search(content, etag_epos)
                if etag_spos is None:
                    raise IncompleteScriptTagError("A server-side script wasn't closed")
                etag_spos = etag_spos.start()
                etag_epos = content.find("%}", etag_spos)
                if etag_epos == -1:
                    raise IncompleteScriptTagError("A server-side tag wasn't closed")
                sfor_cnt = len(reg_exps["startfor"].findall(content, stag_epos, etag_spos))
                efor_cnt = len(reg_exps["endfor"].findall(content, stag_epos, etag_spos))
            content = content[:stag_spos] + content [stag_epos+2:etag_spos] + content[etag_epos:]
        elif script[0] == "if":
            pass
        stag_spos = reg_exps["scriptstart"].search(content,stag_spos)
        if stag_spos is not None:
            stag_spos = stag_spos.start()
        else:
            stag_spos = -1
    #     elif content[stag_pos+1] == "{":
    #         end_tag = content.find("}}", stag_pos)
    #         if end_tag == -1:
    #             raise IncompleteScriptTagError("A server-side script was not closed")
    #         else:
    #             if data is not None:
    #                 data_key = content[stag_pos:end_tag]
    #                 data_key.strip()
    #                 data_key = data_key.split(".")
    #                 if data_key[0] in data.keys():
    #                     data_value = data[data_key[0]]
    #                 data_index = 0
    #                 while data_index < len(data_key):
    #                     if data_key[0] in data.keys():
    #                         data_value = data[data_key[0]]
    #                         if len(data_key) > 1:
    #                             data_value[data_key[1]]
    #                     else:
    #                         index_char = data_key[0].index("[")
    #                         key = data_key[0][:index_char]
    #                         index = data_key[0][index_char+1:-1]
    #                         if key in data.keys():
    #                             data_value = data[key][index]
    #
    #
    #             content = content[:stag_pos] + data_value + content[end_tag + 2:]
    #             pos = end_tag + 2
    return content

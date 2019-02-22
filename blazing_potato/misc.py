import json

def format_result(err, value):
    res = {"errors":err, "result" : value}
    return json.dumps(res)

def sanitize_string_list(str_list: [str]) -> [str]:
    stripped_lines = [line.rstrip().strip() for line in str_list]
    return stripped_lines

def merge_string_list(str_list: [str], sep = '') -> str:
    return sep.join(str_list)

def unformat_str_list(str_list:[str]) -> str:
    return merge_string_list(sanitize_string_list(str_list))

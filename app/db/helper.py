
def escape_special_char(val:str):
    return val.replace('\'', '\'\'').replace('\\', '\\\\')
    
def needs_dollar_quote(val:any) -> str:
    if type(val) is str:
        return '\'%s\'' % escape_special_char(val)
    elif (type(val) is int) or (type(val) is float):
        return '%d' % val
    elif val is None:
        return ''    
    else:
        raise Exception('Unhandled value type: %s' % type(val))     

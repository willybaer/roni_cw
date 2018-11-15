
def escape_special_char(val:str):
    return val.replace('\'', '\'\'').replace('\\', '\\\\')
    
def needs_dollar_quote(val:any, check_for_qoute=False) -> str:
    if not check_for_qoute:
        return '%s' % val
    if type(val) is str:
        return '\'%s\'' % escape_special_char(val)
    elif (type(val) is int) or (type(val) is float):
        return '%d' % val
    elif val is None:
        return ''    
    else:
        raise Exception('Unhandled value type: %s' % type(val))     

def levenshtein_distance(source:str, target:str) -> int:
    v0 = [0] * (len(target) + 1)        
    v1 = [0] * (len(target) + 1)

    for i in range(0, len(target) + 1):
        v0[i] = i

    for i in range(0, len(source)):
        # first element of the target vector is A[i+1][0]
        # edit distance is delete (i+1) chars from s to match empty t
        v1[0] = i + 1     

        for j in range(0, len(target)):
            # calculating costs for A[i+1][j+1]
            deletionCost = v0[j + 1] + 1
            insertionCost = v1[j] + 1
            if source[i] == target[j]:
                substitutionCost = v0[j]
            else:
                substitutionCost = v0[j] + 1

            v1[j + 1] = min(deletionCost, insertionCost, substitutionCost)

        # copy s_v (current row) to s_v (previous row) for next iteration
        a = v1
        v1 = v0
        v0 = a    
    return v0[len(target)]                  

def levenshtein_distance_percentage(source:str, target:str) -> float:
    lev = levenshtein_distance(source=source, target=target)
    return lev / len(target)
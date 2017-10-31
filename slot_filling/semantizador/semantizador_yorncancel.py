import re

def yorncancel(message):
    sim_re = re.compile("[sS][iI][mM]")
    nao_re = re.compile("[nN][aãAÃ][oO]")
    cancel_re = re.compile("[cC][aA][nN][cC][eE][lL][aA][rR]")
    
    flag_sim = re.search(sim_re,message) != None
    flag_nao = re.search(nao_re,message) != None
    flag_cancelar = re.search(cancel_re,message) != None
    
    if flag_sim:
        function = 'accept_or_refuse'
        content = 'accept'
        return function,content
    elif flag_nao:
        function = 'accept_or_refuse'
        content = 'refuse'
        return function,content
    elif flag_cancelar:
        function = 'cancel_event'
        content = ''
        return function,content
    else:
        return None, None
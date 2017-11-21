# função auxiliar utilizada em processLocal() para formatar a URL do request para Places API

def format_url(url, params):
    r_url = url + '?'
    for key in params:
        r_url += key + '=' + params[key] + '&'

    r_url = r_url[:-1]
    return r_url

def translate_relationship(relationship_pre):
    if relationship_pre.split(' ')[0] == 'minha' or relationship_pre.split(' ')[0] == 'meu':
        relationship = ' '.join(relationship_pre.split(' ')[1:])
    else:
        relationship = relationship_pre
    
    if relationship == 'mae' or relationship == 'mãe':
        return('isMotherOf')
    elif relationship == 'tio':
        return('isUncleOf')
    elif relationship == 'tia':
        return('isAuntOf')
    elif relationship == 'primo' or relationship == 'prima':
        return('isCousinOf')
    elif relationship == 'namorado':
        return('isBoyfriendOf')
    elif relationship == 'namorada':
        return('isGirlfriendOf')
    elif relationship == 'vó' or relationship == 'vovó':
        return('isGrandmotherOf')
    elif relationship == 'vô' or relationship == 'vovô':
        return('isGrandfatherOf')
    elif relationship == 'chefe':
        return('isBossOf')
    elif relationship == 'irmão':
        return('isBrotherOf')
    elif relationship == 'irmã':
        return('isSisterOf')
    elif relationship == 'pai':
        return('isFatherOf')
    elif relationship == 'orientador':
        return('isTutorOf')
    
    
    return relationship_pre

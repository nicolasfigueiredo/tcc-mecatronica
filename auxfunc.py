# função auxiliar utilizada em processLocal() para formatar a URL do request para Places API

def format_url(url, params):
	r_url = url + '?'
	for key in params:
		r_url += key + '=' + params[key] + '&'

	r_url = r_url[:-1]
	return r_url
# Classe que define um ato dialogal:
# Contém um campo 'function' e o campo 'content'

class dialog_act:

	def __init__(self, function, content):
		self.function = function
		self.content = content 

	def print(self):
		print('func:' + str(self.function))
		print('content:' + str(self.content))

class dialog_act_extended:
	def __init__(self, function, content, extra_content):
		self.function = function
		self.content = content 
		self.extra_content = extra_content

	def print(self):
		print('func:' + str(self.function))
		print('content:' + str(self.content))
		print('extra content:' + str(self.extra_content))
__all__=['ndict','JsonFile']

class ndict(dict):
	def __getattr__(self,key):
		return self[key]


import json
import os
class JsonFile(dict):
	def __init__(self,filename):
		self.name=filename
		if os.path.exists(filename):
			with open(filename,'r',encoding='utf-8') as f:
				dict.__init__(self,json.load(f))
		else:
			self.update()
	def update(self):
		with open(self.name,'w',encoding='utf-8') as f:
			json.dump(self,f,ensure_ascii=False)

__all__=['sinput','zipall','debug','group','iter_diff']

def sinput(n,s='',sep=None,dtype=str):
	print(s,end='')
	res=[]
	while len(res)<n:
		res.extend(map(dtype,input().split(sep)))
	return res[:n]

def zipall(*iterables,**kwargs):
	if len(kwargs)==0:
		def get_v(*args):
			if len(args)==1:
				return zipall(*iterables,v=args[0])
			else:
				return zipall(*iterables,vs=args)
		return get_v
	key=list(kwargs.keys())[0]
	val=list(kwargs.values())[0]
	if key[-1]!='s':
		val=[val]*len(iterables)
	length=max(map(len,iterables))
	iterables=([*it,*val[i:i+1]*(length-len(it))] for i,it in enumerate(iterables))
	return zip(*iterables)
	
def debug(obj,*,private=False,run=False):
	for i in dir(obj):
		if i!='__globals__' and (private or not i.startswith('_')):
			attr=getattr(obj,i)
			try:
				assert run
				print(repr(i),attr,attr())
			except:
				print(repr(i),attr)

def sbin(n,w=32):
	return ''.join(str(n>>i&1) for i in reversed(range(w)))
	
def group(it,key):
	d={}
	for i in it:
		d.setdefault(key(i),[]).append(i)
	return d
	
from collections import deque
def iter_diff(it,n):
	it=iter(it)
	q=deque(next(it) for _ in range(n-1))
	for i in it:
		q.append(i)
		yield tuple(q)
		q.popleft()
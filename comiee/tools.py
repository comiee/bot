from functools import wraps
from inspect import signature
from typing import get_type_hints

__all__=['autorun','fixed','overload','tag']

def autorun(*args,**kwargs):
	'''装饰后自动执行，args和kwargs是执行时的参数，执行完毕后函数名会变成执行的结果
	Example:
	>>> @autorun(1,2)
	... def f(x,y):
	...     print(x,y)
	...
	1 2
	'''
	def get_func(func):
		return func(*args,**kwargs)
	return get_func


def fixed(*vals,**kwvals):
	'''用于闭包中绑定变量
	与fixed的参数同位置的参数会被视为绑定的变量，其余参数需要在调用时传入
	Example:
	>>> x=233
	>>> @fixed(x)
	... def f(x):
	...     print(x)
	...
	>>> def g():
	... 	print(x)
	...
	>>> x=666
	>>> f()
	233
	>>> g()
	666
	'''
	def get_func(func):
		@wraps(func)
		def wrapper(*args,**kwargs):
			return func(*vals,*args,**kwvals,**kwargs)
		return wrapper
	return get_func


def overload(func,*,funcs={}):
	'''重载函数，不同的参数个数或者类型注解都可以用于重载
	（请无视funcs，这是用来存储重载的函数的）
	Example:
	>>> @overload
	... def f(x:int):
	...     print('int ',x)
	...
	>>> @overload
	... def f(x:str):
	...     print('str ',x)
	...
	>>> @overload
	... def f(x,y):
	...     print('two ',x,y)
	...
	>>> f(233)
	int  233
	>>> f('abc')
	str  abc
	>>> f(1,2)
	two  1 2
	'''
	name=func.__qualname__
	funcs.setdefault(name,[]).append(func)
	@wraps(func)
	def wrapper(*args,**kwargs):
		error_list=[]
		for f in funcs[name]:
			sig=signature(f)
			annotations=get_type_hints(f)
			try:
				bound=sig.bind(*args,**kwargs)
				for k,v in bound.arguments.items():
					if k in annotations and not isinstance(v,annotations[k]):
						raise TypeError(f'参数类型错误：参数{k}应为{annotations[k]!r}，实为{type(v)!r}')
			except TypeError as e:
				error_list.append(f'匹配参数{sig}：{e}')
			else:
				return f(*args,**kwargs)
		raise TypeError('没有符合参数的重载\n'+'\n'.join(error_list))
	wrapper.all=funcs[name]
	wrapper.__doc__='\n\n'.join(f'{name}{signature(f)}\n{f.__doc__}' for f in funcs[name])
	return wrapper


def tag(fun):
	'''实现跨函数返回。被装饰的函数会获得一个ret方法，调用ret就可以返回到该函数
	Example:
	>>> @tag
	... def f():
	...     def g():
	...         f.ret(233)
	...     g()
	...
	>>> f()
	233
	'''
	t=Exception()
	@wraps(fun)
	def wrapper(*args,**kwargs):
		try:
			return fun(*args,**kwargs)
		except Exception as e:
			if e is t:
				return e.res
			raise
	def ret(res):
		t.res=res
		raise t
	wrapper.ret=ret
	return wrapper


if __name__=='__main__':
	import doctest
	doctest.testmod()
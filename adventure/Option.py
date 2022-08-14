from comiee import overload


class Option:
    """选项类
    使用方法：
    class C:
        option=Option()
        @option(key,name,info)
        def func(self):
            # your code
    或：
    option=Option()
    @option(key,name,info)
    def func():
        # your code
    使用option[key]或者option[name]就可以获得装饰的函数
    如果未指定key，则自动按序号生成一个
    注意使用的时候一定要新创建一个实例，不可以直接使用父类的属性"""

    def __init__(self, option=None):
        if option is None:
            self.dict_func = {}  # key->func
            self.dict_name = {}  # name->key
            self.dict_info = {}  # key->info
        else:
            self.dict_func = {**option.dict_func}  # key->func
            self.dict_name = {**option.dict_name}  # name->key
            self.dict_info = {**option.dict_info}  # key->info
        self.key = 1
        self.owner = None

    def __get__(self, instance, owner):
        self.owner = (instance, owner)
        return self

    def __contains__(self, key):
        return key in self.dict_func or key in self.dict_name

    def __getitem__(self, key):
        key = str(key)
        if key not in self.dict_func:
            key = self.dict_name[key]
        func = self.dict_func[key]
        if self.owner is None:
            return func
        else:
            return func.__get__(*self.owner)

    @overload
    def __call__(self, key, name, info=''):
        key = str(key)

        def get_func(func):
            self.dict_func[key] = func
            self.dict_name[name] = key
            self.dict_info[key] = info
            return func

        return get_func

    @overload
    def __call__(self, name, *, info=''):
        return self(self.next_key, name, info)

    @property
    def next_key(self):
        while str(self.key) in self.dict_func:
            self.key += 1
        return self.key

    def __str__(self):
        return '\n'.join(f'{key}: {name}{self.dict_info[key]}' for name, key in
                         sorted(self.dict_name.items(), key=lambda x: (x[1] == '0', x[1])))

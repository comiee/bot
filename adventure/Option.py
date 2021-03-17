class Option:
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

    def __call__(self, key, name=None, info=''):
        if name is None:
            key, name = self.next_key, key
        key = str(key)

        def get_func(func):
            self.dict_func[key] = func
            self.dict_name[name] = key
            self.dict_info[key] = info
            return func

        return get_func

    @property
    def next_key(self):
        while str(self.key) in self.dict_func:
            self.key += 1
        return self.key

    def __str__(self):
        return '\n'.join(f'{key}: {name}{self.dict_info[key]}' for name, key in self.dict_name.items())

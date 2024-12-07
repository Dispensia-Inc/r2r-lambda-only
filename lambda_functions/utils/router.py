import re


class Router():
    def __init__(self):
        self.decorated_functions = {}

    def get(self, path: str):
        def inner(func):
            key = self.gen_func_key('get', path)
            self.decorated_functions[key] = {"path": path, "function": func}
        return inner

    def post(self, path: str):
        def inner(func):
            key = self.gen_func_key('post', path)
            self.decorated_functions[key] = {"path": path, "function": func}
        return inner

    def gen_func_key(self, method: str, path: str):
        # example result: 'get-/documents/{#}/{#}'
        path_segments = path.strip('/').split('/')
        root_segment = path_segments[0]
        segments = "/".join(['{#}']*len(path_segments[1:]))
        return method.lower() + "-" + f"/{root_segment}/{segments}"

    def get_path_params(self, path_pattern: str, request_path: str):
        params_dict = {}
        path_pattern = path_pattern.split('/')
        request_path = request_path.split('/')
        for i in range(len(path_pattern)):
            m = re.match(r"\{[a-z0-9_].*?\}", path_pattern[i])
            if m:
                path_param = re.sub(r"[\{,\}]", '', path_pattern[i])
                params_dict[path_param] = request_path[i]

        return params_dict

    async def handler(self, event):
        method = event["httpMethod"]
        path = event["path"]
        key = self.gen_func_key(method, path)
        target = self.decorated_functions[key]
        kwargs = self.get_path_params(target['path'], path)
        return await target['function'](**kwargs)

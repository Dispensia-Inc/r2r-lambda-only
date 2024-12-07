import re
import json


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

    def gen_func_key(self, method: str, path: str) -> str:
        # example result: 'get-/documents/{#}/{#}'
        path_segments = path.strip('/').split('/')
        root_segment = path_segments[0]
        segments = "/".join(['{#}']*len(path_segments[1:]))
        return method.lower() + "-" + f"/{root_segment}/{segments}"

    def get_path_params(self, path_pattern: str, request_path: str) -> dict:
        params_dict = {}
        path_pattern = path_pattern.split('/')
        request_path = request_path.split('/')
        for i in range(len(path_pattern)):
            m = re.match(r"\{[a-z0-9_].*?\}", path_pattern[i])
            if m:
                path_param = re.sub(r"[\{,\}]", '', path_pattern[i])
                params_dict[path_param] = request_path[i]

        return params_dict

    def get_body(body: str, keys: list[str]) -> dict:
        body = json.loads(body)
        res = {}
        for key in keys:
            res[key] = body[key] if key in body.keys() else None
        return res

    async def handler(self, event):
        method: str = event["httpMethod"]
        path: str = event["path"]
        headers: str = event["headers"]
        body: dict = json.dumps(event["body"])

        key = self.gen_func_key(method, path)
        target = self.decorated_functions[key]
        kwargs = self.get_path_params(target['path'], path)
        kwargs = {
            'headers': headers,
            'body': body,
            **kwargs
        }
        return await target['function'](**kwargs)


if __name__ == '__main__':
    router = Router()

    @router.get('/documents/{id}/{document_id}/chunk')
    def get_documents(id: str, document_id: str):
        print("ドキュメントの取得: id=", id)
        print("ドキュメントの取得: document_id=", document_id)

    @router.post('/documents/{id}/{document_id}/chunk')
    def update_documents(id: str, document_id: str):
        print("ドキュメントの更新: id=", id)
        print("ドキュメントの更新: document_id=", document_id)

    payload = {"httpMethod": "GET",
               "path": "/documents/sidf0930-s9d90/sd89sd0-sasd3a/chunk"}
    router.handler(payload)

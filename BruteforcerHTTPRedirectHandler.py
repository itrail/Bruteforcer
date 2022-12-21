from urllib.request import HTTPRedirectHandler


class BruteforcerHTTPRedirectHandler(HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.redirects = []

    def redirect_request(self, req, fp, code, msg, headers, newUrl):
        self.redirects.append(headers["location"])
        return super().redirect_request(req, fp, code, msg, headers, newUrl)

    def get_redirects(self):
        return self.redirects

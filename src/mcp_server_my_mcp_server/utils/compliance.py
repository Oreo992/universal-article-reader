from urllib.parse import urlparse, parse_qs, urlunparse


WECHAT_HOST = "mp.weixin.qq.com"


def is_public_wechat_article(url: str) -> bool:
    """
    Basic whitelist: only accept mp.weixin.qq.com /s links.
    This is a heuristic; more rules can be added.
    """
    try:
        u = urlparse(url)
        if u.scheme not in ("http", "https"):
            return False
        if u.hostname != WECHAT_HOST:
            return False
        # common paths: /s, /s/xxx, /s?__biz=...
        return u.path.startswith("/s")
    except Exception:
        return False


def strip_tracking_params(url: str) -> str:
    """
    Remove obvious tracking parameters.
    (This is a minimal example; real rules may need expansion.)
    """
    try:
        u = urlparse(url)
        q = parse_qs(u.query, keep_blank_values=True)
        for k in ["chksm", "scene", "utm_source", "utm_medium", "utm_campaign"]:
            q.pop(k, None)
        # rebuild query
        query = "&".join(f"{k}={','.join(v)}" for k, v in q.items())
        clean = urlunparse((u.scheme, u.netloc, u.path, u.params, query, u.fragment))
        return clean
    except Exception:
        return url
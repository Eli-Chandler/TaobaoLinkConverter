import urllib.parse
from urllib.parse import urlparse, parse_qs
import re

MATCHING_RULES = {
    'TAOBAO': ('item.taobao.com', 'detail.tmall.com', 'm.intl.taobao.com', 'h5.m.taobao.com', 'world.taobao.com', 'shop.m.taobao.com'),
    'WEIDIAN': ('weidian.com', 'shop.*\.v\.weidian\.com'),
    'SIXTEEN88': ('m.1688.com', 'detail.1688.com'),
    'KYOUSHOP': ('k.youshop10.com',),
    'TMALL': ('m.tb.cn', 'tmall.com'),
    'PANDABUY': ('pandabuy.com', 'www.pandabuy.com')
}

URL_CREATORS = {
    'TAOBAO': lambda url: 'https://item.taobao.com/item.htm?id=' + parse_qs(url.query)['id'][0] if 'id' in parse_qs(url.query) else False,
    'WEIDIAN': lambda url: 'https://weidian.com/item.html?itemID=' + parse_qs(url.query)['itemID'][0] if 'itemID' in parse_qs(url.query) else False,
    'SIXTEEN88': lambda url: 'https://detail.1688.com' + url.path if re.match('/offer/\d{12}\.html', url.path) else False,
    'KYOUSHOP': lambda url: url,
    'TMALL': lambda url: url
}

def match_url(hostname):
    for key, urls in MATCHING_RULES.items():
        if any(re.search(url, hostname) for url in urls):
            return key
    return None

def get_url(url):
    url = urlparse(url)

    if not url.hostname:
        return None

    parsed_url = match_url(url.hostname)
    if parsed_url:
        if parsed_url in URL_CREATORS:
            return URL_CREATORS[parsed_url](url)
        elif parsed_url == 'PANDABUY':
            qs = parse_qs(url.query)
            if 'url' in qs:
                return get_url(urllib.parse.unquote(qs['url'][0]))
    return None

if __name__ == '__main__':
    print(get_url('https://weidian.com/item.html?itemID=3087428505&sku=0:48967469525&sku_id=48967469525'))
    print(get_url('https://item.taobao.com/item.htm?id=637720840003'))
    print(get_url('https://youtube.com'))
    print(get_url(''))
    print(get_url('https://shop1707804864.v.weidian.com/item.html?itemID=3087428505&sku=0:48967469525&sku_id=48967469525'))
    print(get_url('https://www.pandabuy.com/product?ra=762&url=https%3A%2F%2Fweidian.com%2Fitem.html%3FitemID%3D3087428505%26sku%3D0%3A48967469525%26sku_id%3D48967469525&utm_source=url&utm_medium=pdb&utm_campaign=normal'))
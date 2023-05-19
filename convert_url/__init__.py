import urllib.parse
from urllib.parse import urlparse, parse_qs
import re
import aiohttp


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
    'TMALL': lambda url: url
}

def match_url(hostname):
    for key, urls in MATCHING_RULES.items():
        if any(re.search(url, hostname) for url in urls):
            return key
    return None

async def get_url(url):
    url = urlparse(url)

    if not url.hostname:
        return None

    parsed_url = match_url(url.hostname)
    if parsed_url:
        if parsed_url in URL_CREATORS:
            return URL_CREATORS[parsed_url](url)
        elif parsed_url == 'KYOUSHOP':
            async with aiohttp.ClientSession() as session:
                headers = {
                    'authority': 'k.youshop10.com',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-language': 'en-US,en;q=0.9',
                    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                }
                r = await session.get(url.geturl(), headers=headers)

                if r.status == 200:
                    return 'https://weidian.com/item.html?itemID=' + r.url.query.get('itemID')
                else:
                    return None



        elif parsed_url == 'PANDABUY':
            qs = parse_qs(url.query)
            if 'url' in qs:
                return get_url(urllib.parse.unquote(qs['url'][0]))
    return None

async def main():
    print(await get_url('https://k.youshop10.com/p3wixRer?a=b&p=iphone&wfr=BuyercopyURL&share_relation=8c817685cedb7891_215732834_1'))

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
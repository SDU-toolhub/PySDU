from login import *

def bkzhjx_login(username, password, platform_info: dict = {}):
    sso_redirect = httpx.get(r'http://bkzhjx.wh.sdu.edu.cn/sso.jsp')
    # print(sso_redirect.headers, sso_redirect.cookies)
    sso_redirect = httpx.get(sso_redirect.headers['Location'])
    # print(sso_redirect.headers, sso_redirect.cookies)

    bzb_njw = sso_redirect.cookies['bzb_njw']
    SERVERID = sso_redirect.cookies['SERVERID']

    page2 = webpage_login(username, password, platform_info, r'http%3A%2F%2Fbkzhjx.wh.sdu.edu.cn%2Fsso.jsp')
    if page2.status_code == 200:
        print(page2.cookies)
    redirect_url = page2.headers['Location']
    # print(page2.headers, page2.status_code)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Upgrade-Insecure-Requests':'1',
    }
    page = httpx.get(redirect_url, headers=headers)
    # print(page.headers, page.status_code)
    
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection':'keep-alive',
        'Cookie':f'SERVERID={SERVERID}; bzb_njw={bzb_njw}',
        'Host':'bkzhjx.wh.sdu.edu.cn',
        'Referer':redirect_url,
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-site',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
    }

    cookies = httpx.Cookies()
    cookies.set("SERVERID", SERVERID, path="/", domain="bkzhjx.wh.sdu.edu.cn")
    cookies.set('bzb_njw', bzb_njw, path="/", domain="bkzhjx.wh.sdu.edu.cn")

    redirect_page = httpx.get(page.headers['Location'], headers=headers, cookies=cookies)
    # print(redirect_page.headers, redirect_page.status_code)
    # cookies = page.cookies
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection':'keep-alive',
        'Cookie':f'SERVERID={SERVERID}; bzb_njw={bzb_njw}',
        'Host':'bkzhjx.wh.sdu.edu.cn',
        # 'Referer':redirect_page.headers['Location'],
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-site',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
    }

    sso_page = httpx.get(redirect_page.headers['Location'], headers=headers, cookies=cookies)
    # print(sso_page.headers, sso_page.status_code)
    while sso_page.status_code == 302:
        redirect_url = sso_page.headers['Location']
        headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection':'keep-alive',
            'Cookie':f'SERVERID={SERVERID}; bzb_njw={bzb_njw}',
            'Host':'bkzhjx.wh.sdu.edu.cn',
            'Referer':redirect_page.headers['Location'],
            'Sec-Fetch-Dest':'document',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-Site':'same-site',
            'Sec-Fetch-User':'?1',
            'Upgrade-Insecure-Requests':'1',
        }
        # print(redirect_url, cookies)
        sso_page = httpx.get(redirect_url, headers=headers, cookies=cookies)
        cookies = sso_page.cookies
        if cookies.get('bzb_jsxsd') is not None:
            break
    bzb_jsxsd = cookies['bzb_jsxsd']
    cookies = httpx.Cookies()
    cookies.set("SERVERID", SERVERID, path="/", domain="bkzhjx.wh.sdu.edu.cn")
    cookies.set('bzb_njw', bzb_njw, path="/", domain="bkzhjx.wh.sdu.edu.cn")
    cookies.set('bzb_jsxsd', bzb_jsxsd, path="/", domain="bkzhjx.wh.sdu.edu.cn")
    redirect_url = sso_page.headers['Location']
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        # 'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie':f'SERVERID={SERVERID}; bzb_njw={bzb_njw}; bzb_jsxsd={bzb_jsxsd}',
        'Host':'bkzhjx.wh.sdu.edu.cn',
        'Referer':redirect_page.headers['Location'],
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-site',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
    }
    page = httpx.get(redirect_url, cookies=cookies, headers=headers)

    if page.status_code == 200:
        return cookies
    
    else:
        raise SystemError('Launch bkzhjx.wh.sdu.edu.cn failed.')
    

if __name__ == '__main__':
    import getpass
    username = input('学号：')
    password = getpass.getpass('密码：')

    cookie = bkzhjx_login(username, password, {'1':'2'})

    page = httpx.get(r'https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/xsMainV_new.htmlx?t1=1', cookies=cookie)
    if page.status_code == 200:
        print('登录成功，已获取课程列表页面')
    with open('export/course_list.html', 'w', encoding='utf-8') as f:
        f.write(page.text)
    
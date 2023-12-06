import bs4, datetime
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

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Upgrade-Insecure-Requests':'1',
    }
    page = httpx.get(redirect_url, headers=headers)

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


def get_timetable(cookie):
    def main(rq, semester = '', kbjcmsid = ''):
        nonlocal cookie
        url = f'https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/mainV_index_loadkb.htmlx?rq={rq}'
        if semester:
            url += f'&xnxqid={semester}'
        if kbjcmsid:
            url += f'&sjmsValue={kbjcmsid}'
        url += '&xswk=false'
        page = httpx.get(url, cookies=cookie)
        if page.status_code == 200:
            print('已获取本周课表：')
        page = bs4.BeautifulSoup(page.text, 'html.parser')
        lessons = page.findAll('td')
        for lesson in lessons:
            c = lesson.findAll('div')
            if len(c) == 0:
                continue
            name = c[0].find('p').text
            credit = c[1].findAll('span')[0].text
            time = c[1].findAll('span')[1].text
            loc = c[2].findAll('span')[0].text
            # remove the img before loc
            loc = re.sub(r'<img.*?>', '', str(loc))
            week = c[2].findAll('span')[1].text
            week = re.sub(r'<img.*?>', '', str(week))
            print(name, credit, time, loc, week)
        return True
    rq = datetime.datetime.now().strftime('%Y-%m-%d')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if 0 < month < 7:
        year -= 1
        sem = 2
    elif 7 <= month <= 8:
        sem = 3
        year -= 1
    else:
        sem = 1
    semester = f'{year}-{year + 1}-{sem}'
    try:
        #  url = f'https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/mainV_index_loadkb.htmlx?rq={rq}&sjmsValue={kbjcmsid}&xnxqid={semester}&xswk=false'
        assert main(rq, semester)
    except Exception as exc:
        print(f'拉取课程表失败——{exc}')
        try: 
            page = httpx.get(r'https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/xsMainV_new.htmlx?t1=1', cookies=cookie)
            if page.status_code == 200:
                print('尝试拉取所有课程：')
            page = bs4.BeautifulSoup(page.text, 'html.parser')
            try:
                kbjcmsid = page.find(id='kbjcmsid_ul').findAll('li')[0].attrs['data-value']
                assert main(rq, semester, kbjcmsid)
            except Exception as exc:
                print(f'第二次尝试拉取课程列表失败——{exc}')
            else:
                return
            print('尝试仅拉取课程信息：')
            lessons = page.findAll('td')
            k=0
            for lesson in lessons:
                if span:=lesson.find('span').text:
                    k+=1
                    if k%3==1:
                        print(span, end=' ')  # course name
                    elif k%3==2:
                        print(span)  # course teacher
        except Exception:
            raise SystemError('Launch bkzhjx.wh.sdu.edu.cn failed.')
    finally:
        return

if __name__ == '__main__':
    try:
        with open("bkzhjx_cookies.json", "r") as f:
            cookies = json.load(f)
            cookie = httpx.Cookies(cookies)
        page = httpx.get(r'https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/xsMainV_new.htmlx?t1=1', cookies=cookie)
        assert page.status_code == 200
    except Exception as e:
        print('未找到有效cookies，将重新登录')
        import getpass

        username = input('学号：')
        password = getpass.getpass('密码：')
        with open("fingerprint.json", "r") as f:
            fake_platoform_fingerprint = json.load(f)
        cookie = bkzhjx_login(username, password, fake_platoform_fingerprint)
        out = {}
        for k, v in cookie.items():
            out[k] = v
        with open("bkzhjx_cookies.json", "w") as f:
            json.dump(out, f)
    else:
        print('cookies有效，免输入密码')
    finally:
        get_timetable(cookie)

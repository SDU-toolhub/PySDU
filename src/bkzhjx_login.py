import json
import os, sys, re
import bs4, datetime
import httpx
from httpx import Cookies
from login import webpage_login
import csv

def bkzhjx_login(username, password, platform_fingerprint: str) -> Cookies:
    """
    Login to bkzhjx.wh.sdu.edu.cn, and return the cookies.
    """
    sso_redirect = httpx.get(r'http://bkzhjx.wh.sdu.edu.cn/sso.jsp')
    # print(sso_redirect.headers, sso_redirect.cookies)
    sso_redirect = httpx.get(sso_redirect.headers['Location'])
    # print(sso_redirect.headers, sso_redirect.cookies)

    bzb_njw = sso_redirect.cookies['bzb_njw']
    SERVERID = sso_redirect.cookies['SERVERID']

    page2 = webpage_login(username, password, platform_fingerprint, r'http%3A%2F%2Fbkzhjx.wh.sdu.edu.cn%2Fsso.jsp')
    if page2.status_code != 302:
        print('Check your username and password.')
        raise SystemError('Login failed: No redirect. to bkzhjx.wh.sdu.edu.cn')
    redirect_url = page2.headers['Location']
    page = httpx.get(redirect_url)

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

    sso_page = httpx.get(redirect_page.headers['Location'], headers=headers, cookies=cookies)

    while sso_page.status_code == 302:
        redirect_url = sso_page.headers['Location']
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
    headers['Cookie'] = f'SERVERID={SERVERID}; bzb_njw={bzb_njw}; bzb_jsxsd={bzb_jsxsd}'
    page = httpx.get(redirect_url, cookies=cookies, headers=headers)

    if page.status_code == 200:
        return cookies
    
    else:
        raise SystemError('Launch https://bkzhjx.wh.sdu.edu.cn failed.')


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
                kbjcmsid = page.find(id='kbjcmsid_ul').findAll('li')[0].attrs['data-value']  # type: ignore
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
            raise SystemError('Launch https://bkzhjx.wh.sdu.edu.cn failed.')
    finally:
        return

def get_score(cookie, semester, csv_file = "output.csv"):
    url = "https://bkzhjx.wh.sdu.edu.cn/jsxsd/kscj/cjcx_list"
    headers = {
        "Cookie": f"bzb_jsxsd={cookie['bzb_jsxsd']}; SERVERID={cookie['SERVERID']}; bzb_njw={cookie['bzb_njw']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    }
    data = {"kksj": semester, "kcxz": "", "kcmc": "", "xsfs": "all", "sfxsbcxq": "1"}

    response = httpx.post(url, headers=headers, data=data)

    if response.status_code == 200:
        # 解析 HTML
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        table:bs4.Tag = soup.find("table", id="dataList")  # type: ignore
        if not isinstance(table, bs4.Tag):
            return "Error: No table found. Maybe login has expired."
        rows = table.find_all("tr")

        data = []

        header = rows[0].find_all("th")
        header = [col.text.strip() for col in header]
        data.append(header[1:])

        for row in rows[1:]:
            cols = row.find_all("td")
            cols = [col.text.strip() for col in cols]
            data.append(cols[1:])

        
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

        print(f"数据已写入 {csv_file} 文件中。")

    else:
        return f"Error: {response.status_code} HTTP response."

def interactive_login():
    
    import getpass


    # check if fingerprint file exists
    if not os.path.exists("Fingerprint.txt"):
        # create fingerprint file which should be empty at first
        with open("Fingerprint.txt", "w", encoding='utf-8') as f:
            f.write("")
        print("生成默认指纹文件，请修改Fingerprint.txt中的信息后重新运行；或者使用空指纹登录。")
        print("指纹文件路径：", os.path.abspath("Fingerprint.txt"))
        print("此文件作为设备的标志。其内容如果不改变，就不必重复输入短信验证码。如果更换设备，可以直接拷贝走这个文件。")
    with open("Fingerprint.txt", "r", encoding='utf-8') as f:
        fake_platoform_fingerprint = f.read()
    if not fake_platoform_fingerprint:
        if not input("当前指纹文件为空。指纹文件存放在："+os.path.abspath("Fingerprint.txt")+"\n是否继续运行程序并使用空指纹作为设备标志？(y/N)") == "y":
            sys.exit(0)
    username = input('学号：')
    password = getpass.getpass('密码：')
    cookie: Cookies = bkzhjx_login(username, password, fake_platoform_fingerprint)
    out = dict(cookie.items())
    with open("bkzhjx_cookies.json", "w") as f:
        json.dump(out, f)
    print('登录成功，cookies已保存至bkzhjx_cookies.json')
    return cookie

if __name__ == '__main__':
    try:
        with open("bkzhjx_cookies.json", "r") as f:
            cookies = json.load(f)
            cookie = httpx.Cookies(cookies)
        page = httpx.get(r'https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/xsMainV_new.htmlx?t1=1', cookies=cookie)
        assert page.status_code == 200
        assert bs4.BeautifulSoup(page.text, 'html.parser').title.text != '登录'  # type: ignore
    except Exception as e:
        print('未找到有效cookies，将重新登录')
        cookie = interactive_login()
    else:
        print('cookies有效，免输入密码')
    
    get_timetable(cookie)
    get_score(cookie,'', csv_file='score.csv')

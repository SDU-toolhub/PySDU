import json
import httpx
import xml.dom.minidom
from .uniform_login_des import strEnc
import re
import hashlib


def x64hash128(s, seed):
    return hashlib.blake2b(s.encode('utf-8'), digest_size=16, key=seed.to_bytes(16, 'big')).hexdigest()

def hex_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def restful_login(username, password, baseURL="https://pass.sdu.edu.cn/") -> str:
    """
    Using the RESTful API to login, powered by httpx.

    Recommended, but how to use it in webpages other than the CAS built in APIs is unknown so far.
    """
# 发送第一个请求，获取ticket
    ticket = httpx.post(
        f"{baseURL}cas/restlet/tickets",
        content=f"username={username}&password={password}&lt=LT-1-1-1",
    ).text
    if not ticket.startswith("TGT"):
        raise Exception("ticket should start with TGT. Check your username and password.")
    # 发送第二个请求，获取sTicket
    sTicket = httpx.post(f"{baseURL}cas/restlet/tickets/{ticket}",content="service=https://service.sdu.edu.cn/tp_up/view?m=up", headers={"Content-Type": "text/plain"}).text
    # print("sTicket: " + sTicket)
    # 检查sTicket是否以ST开头
    if not sTicket.startswith("ST"):
        raise Exception("sTicket should start with ST")
    return sTicket


def get_user_name_and_id(sTicket, baseURL="https://pass.sdu.edu.cn/"):
    """
    An example of how to use the RESTful API to get user name and id from the CAS API.

    Can be used to check password.
    """
    user_data = xml.dom.minidom.parseString(httpx.get(
        f"{baseURL}cas/serviceValidate",
        params={
            "ticket": sTicket,
            "service": "https://service.sdu.edu.cn/tp_up/view?m=up",
        },
    ).text)
    name = user_data.getElementsByTagName("cas:USER_NAME")[0].childNodes[0].data
    student_id = user_data.getElementsByTagName("sso:user")[0].childNodes[0].data
    return name, student_id


def webpage_login(username: str, password: str, platform_info: dict = {}, service:str = ''):
    """
    Using webpage to login, powered by execjs, BeautifulSoup4 to parse the html and httpx to send requests.
    """
    if service:
        page = httpx.get(f"https://pass.sdu.edu.cn/cas/login?service={service}")
    else:
        page = httpx.get(r"https://pass.sdu.edu.cn/cas/login")
    lt = re.findall(r'name="lt" value="(.*?)"', page.text)[0]
    ul = len(username)
    pl = len(password)
    rsa = strEnc(username + password + lt, "1", "2", "3")
    execution = re.findall(r'name="execution" value="(.*?)"', page.text)[0]
    event_id = re.findall(r'name="_eventId" value="(.*?)"', page.text)[0]
    # platform_info = {str(random.randint(0, 100)): str(random.randint(0, 100)) for _ in range(10)}
    content = f"rsa={rsa}&ul={ul}&pl={pl}&lt={lt}&execution={execution}&_eventId={event_id}"
    det = "\n".join(f"{x} = {y}"[:100] for x, y in platform_info.items())
    murmur = x64hash128("".join(platform_info.values()), 31)
    murmur_s = x64hash128(det, 31)
    murmur_md5 = hex_md5(murmur_s)
    body1 = {
        'u': strEnc(username, "1", "2", "3"),
        'p': strEnc(password, "1", "2", "3"),
        'm': '1',   # mode 1 to get if device registered
        'd': murmur,    # x64hash128 of values of platform_info
        'd_s': murmur_s,  # x64hash128 of str[:100] of lines 'key = value' of platform_info
        'd_md5': murmur_md5 # md5 of d_s
    }
    device_status = httpx.post(r'https://pass.sdu.edu.cn/cas/device', data=body1, cookies=page.cookies)
    device_status_dict = json.loads(device_status.text)

    match device_status_dict.get('info'):
        case 'binded' | 'pass':
            pass
        case 'bind':
            print('2FA:' + device_status_dict.get('m'))
            tmp = httpx.post(
                r'https://pass.sdu.edu.cn/cas/device',
                data={'m': '2'},
                cookies=page.cookies,
            )
            if tmp.text == r'{"info":"send"}':
                print('已发送验证码')
            else:
                raise SystemError(f'Unknown SMS status: {tmp.text}')
            body3 = {
                'd': murmur_s,
                'i': det,
                'm': '3',
                'u': username,
                'c': input('请输入验证码：'),
                's': '1' if input('下次不再输入验证码？(y/N)：') == 'y' else '0',
            }
            k = httpx.post(
                r'https://pass.sdu.edu.cn/cas/device',
                data=body3,
                cookies=page.cookies,
            )
            while k.text == r'{"info":"codeErr"}':
                body3['c'] = input('验证码错误，请重新输入：')
                k = httpx.post(
                    r'https://pass.sdu.edu.cn/cas/device',
                    data=body3,
                    cookies=page.cookies,
                )
            if k.text == r'{"info":"ok"}':
                print('验证成功')
                if body3['s'] == '1':
                    print(f'对于设备信息：{platform_info}，下次登录将不再需要验证码')
        case _:
            print(
                'Please check your username. Device information cannot be loaded by SDU pass.'
            )
            raise SystemError(
                f'Unknown device status: {str(device_status_dict)}'
            )
    cookies = page.cookies
    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'Accept-Encoding':'gzip, deflate, br',
        # 'Accept-Language':'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
        # 'Cache-Control':'max-age=0',
        # 'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
        # 'Cookie': 'JSESSIONID='+page.cookies['JSESSIONID']+'; Language=zh_CN; cookie-adx='+page.cookies['cookie-adx'],
        # 'Host':'pass.sdu.edu.cn',
        # 'Origin':'https://pass.sdu.edu.cn',
        # 'Referer':r'https://pass.sdu.edu.cn/cas/login?service=http%3A%2F%2Fbkzhjx.wh.sdu.edu.cn%2Fsso.jsp',
        # 'Sec-Ch-Ua':'"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        # 'Sec-Ch-Ua-Mobile':'?0',
        # 'Sec-Ch-Ua-Platform':'"Windows"',
        # 'Sec-Fetch-Dest':'document',
        # 'Sec-Fetch-Mode':'navigate',
        # 'Sec-Fetch-Site':'same-origin',
        # 'Sec-Fetch-User':'?1',
        # 'Upgrade-Insecure-Requests':'1',
        # 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    }
    page2 = httpx.post(r"https://pass.sdu.edu.cn/cas/login?service=http%3A%2F%2Fbkzhjx.wh.sdu.edu.cn%2Fsso.jsp", content=content, cookies=cookies, headers=headers)
    if page2.status_code in [302, 200]:
        return page2
    else:
        raise SystemError('Login to pass.sdu.edu.cn failed.')

import getpass
import os
import sys
import json
import httpx
import xml.dom.minidom
from .uniform_login_des import strEnc
import re
import hashlib


def restful_login(username, password, baseURL="https://pass.sdu.edu.cn/") -> str:
    """
    Using the RESTful API to login, powered by httpx.

    Recommended, but how to use it in webpages other than the CAS built in APIs is unknown so far.
    """
    # 发送第一个请求，获取ticket
    ticket = httpx.post(
        f"{baseURL}cas/restlet/tickets",
        content=f"username={username}&password={password}",
    ).text
    if not ticket.startswith("TGT"):
        raise Exception(
            "ticket should start with TGT. Check your username and password."
        )
    # 发送第二个请求，获取sTicket
    sTicket = httpx.post(
        f"{baseURL}cas/restlet/tickets/{ticket}",
        content="service=https://service.sdu.edu.cn/tp_up/view?m=up",
        headers={"Content-Type": "text/plain"},
    ).text
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
    user_data = xml.dom.minidom.parseString(
        httpx.get(
            f"{baseURL}cas/serviceValidate",
            params={
                "ticket": sTicket,
                "service": "https://service.sdu.edu.cn/tp_up/view?m=up",
            },
        ).text
    )
    name = user_data.getElementsByTagName("cas:USER_NAME")[0].childNodes[0].data
    student_id = user_data.getElementsByTagName("sso:user")[0].childNodes[0].data
    return name, student_id


def webpage_login(
    username: str, password: str, platform_fingerprint: str, service: str = ""
):
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
    content = (
        f"rsa={rsa}&ul={ul}&pl={pl}&lt={lt}&execution={execution}&_eventId={event_id}"
    )
    det = platform_fingerprint
    murmur = platform_fingerprint
    murmur_s = ""   # this is not checked by the server, so we can use an empty string
    murmur_md5 = hashlib.md5(murmur.encode('utf-8')).hexdigest()
    body1 = {
        "u": strEnc(username, "1", "2", "3"),
        "p": strEnc(password, "1", "2", "3"),
        "m": "1",  # mode 1 to get if device registered
        "d": murmur,
        "d_s": murmur_s,
        "d_md5": murmur_md5,  # md5 of d_s
    }
    device_status = httpx.post(
        r"https://pass.sdu.edu.cn/cas/device", data=body1, cookies=page.cookies
    )
    device_status_dict = json.loads(device_status.text)

    match device_status_dict.get("info"):
        case "binded" | "pass":
            pass
        case "bind":
            print("2FA:" + device_status_dict.get("m"))
            tmp = httpx.post(
                r"https://pass.sdu.edu.cn/cas/device",
                data={"m": "2"},
                cookies=page.cookies,
            )
            if tmp.text == r'{"info":"send"}':
                print("已发送验证码")
            else:
                raise SystemError(f"Unknown SMS status: {tmp.text}")
            body3 = {
                "d": murmur_s,
                "i": det,
                "m": "3",
                "u": username,
                "c": input("请输入验证码："),
                "s": "1" if input("下次不再输入验证码？(y/N)：") == "y" else "0",
            }
            k = httpx.post(
                r"https://pass.sdu.edu.cn/cas/device",
                data=body3,
                cookies=page.cookies,
            )
            while k.text == r'{"info":"codeErr"}':
                body3["c"] = input("验证码错误，请重新输入：")
                k = httpx.post(
                    r"https://pass.sdu.edu.cn/cas/device",
                    data=body3,
                    cookies=page.cookies,
                )
            if k.text == r'{"info":"ok"}':
                print("验证成功")
                if body3["s"] == "1":
                    print(
                        f"对于设备指纹：{platform_fingerprint}，下次登录将不再需要验证码"
                    )
        case _:
            print(
                "Please check your username. Device information cannot be loaded by SDU pass."
            )
            raise SystemError(
                "Unknown device status: {}".format(str(device_status_dict))
            )
    cookies = page.cookies
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    page2 = httpx.post(
        r"https://pass.sdu.edu.cn/cas/login?service=http%3A%2F%2Fbkzhjx.wh.sdu.edu.cn%2Fsso.jsp",
        content=content,
        cookies=cookies,
        headers=headers,
    )
    if page2.status_code == 302:
        return page2
    else:
        raise SystemError("Login to pass.sdu.edu.cn failed.")

def get_username_and_password_from_stdin() -> tuple[str, str, str]:
    """
    Get username and password from stdin, and get the platform fingerprint from Fingerprint.txt.
    """
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
    return username, password, fake_platoform_fingerprint

import httpx
import json
import bs4
from typing import Literal
from bkzhjx_login import interactive_login


def search_course(
    q: str,
    cookies: httpx.Cookies,
    course_type: Literal["Bx",  # 必修
                          "Xx", # 限选
                          "Ggxxk", # 公共选修课（任选）
                          "Faw"] = "Faw",  # 所有课程
    count: int = 100,
) -> httpx.Response:
    """
    Search course by keyword.
    """
    url = f"https://bkzhjx.wh.sdu.edu.cn/jsxsd/xsxkkc/xsxk{course_type}xk?1=1&kcxx={q}&skls=&skxq=&skjc=&endJc=&sfym=false&sfct=true&sfxx=true&skfs=&xqid="
    return httpx.post(
        url,
        data={
            "sEcho": "1",  # 页数
            "iColumns": "14",  # 列数
            "sColumns": "",  # 列名
            "iDisplayStart": "0",  # 起始位置
            "iDisplayLength": str(count),  # 结束位置
            "mDataProp_0": "kch",  # 课程号
            "mDataProp_1": "kcmc",  # 课程名称
            "mDataProp_2": "kchnew",  # 课程号
            "mDataProp_3": "dwmc",  # 开课单位名称
            "mDataProp_4": "jkfs",  # 讲课方式
            "mDataProp_5": "xmmc",  # 项目名称
            "mDataProp_6": "fzmc",  # 分组名称
            "mDataProp_7": "ktmc",  # 课题名称
            "mDataProp_8": "xf",  # 学分
            "mDataProp_9": "skls",  # 上课老师
            "mDataProp_10": "sksj",  # 上课时间
            "mDataProp_11": "skdd",  # 上课地点
            "mDataProp_12": "xqmc",  # 校区名称
            "mDataProp_13": "syrs",  # 剩余人数
            "mDataProp_14": "ctsm",  # 冲突
            "mDataProp_15": "czOper",  # 操作
        },
        cookies=cookies,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
        },
    )


if __name__ == "__main__":
    try:
        with open("bkzhjx_cookies.json", "r") as f:
            cookies = json.load(f)
            cookie = httpx.Cookies(cookies)
        page = httpx.get(
            r"https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/xsMainV_new.htmlx?t1=1",
            cookies=cookie,
        )
        assert page.status_code == 200
        assert bs4.BeautifulSoup(page.text, "html.parser").title.text != "登录"  # type: ignore
    except Exception as e:
        print("未找到有效cookies，将重新登录")
        cookie = interactive_login()
    else:
        print("cookies有效，免输入密码")

    response = search_course("Unix", cookie)
    print(response.text)

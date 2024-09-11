"""
Might be deprecated. Previously used to get if a classroom is available.
"""

from login import webpage_login
import json, httpx, datetime
from typing import Iterable


def pcms_login(username:str, password:str, platform_info: str):
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }
    sso_redirect = httpx.get(r'https://pcms.sdu.edu.cn/tp_crp/view?m=crp', headers=headers)
    sso_redirect = httpx.get(sso_redirect.headers['Location'])
    page = webpage_login(username, password, platform_info, r'https%3A%2F%2Fpcms.sdu.edu.cn%2Ftp_crp%2Fview%3Fm%3Dcrp')
    if page.status_code != 302:
        print('Check your username and password.')
        raise SystemError('Login failed: No redirect. to pcms.sdu.edu.cn')
    redirect_url = page.headers['Location']
    page = httpx.get(redirect_url, headers=headers)
    if page.status_code != 302:
        print(f'Server error.{page.status_code}')
        raise SystemError('Login failed: No redirect to pcms.sdu.edu.cn')
    JSSESSIONID = page.cookies['JSESSIONID']
    cookies = httpx.Cookies()
    cookies.set('JSESSIONID', JSSESSIONID, path='/tp_crp', domain='pcms.sdu.edu.cn')
    page = httpx.get(page.headers['Location'], headers=headers, cookies=cookies)
    if page.status_code != 200:
        print(f'Server error.{page.status_code}')
        raise SystemError('Login failed: No redirect to pcms.sdu.edu.cn')
    return cookies

def get_classroom_data(cookies: httpx.Cookies, date: str = '', area:Iterable[str] | None = None, building:Iterable[str] | None = None, room:Iterable[str] | None = None):
    """
    To get classroom data.

    Args:
        cookies (httpx.Cookies): Cookies of pcms.sdu.edu.cn.
        date (str, optional): Date. Defaults to ''.
        area (list[str], optional): Area. Defaults to [].
        building (list[str], optional): Building. Defaults to [].
        room (list[str], optional): Room. Defaults to [].
    """
    ret = []
    area = area or ['school_area_all']
    for j in area:
        if building or room:
            raise NotImplementedError('Not implemented.')
        data = httpx.post(
            'https://pcms.sdu.edu.cn/tp_crp/crp/scra/getClassRoomList',
            content = json.dumps({
                'COLLECTED': 'all',
                'JSMC' : '',
                'LDMC' : '',
                'USE_DATE' : date or datetime.datetime.now().strftime('%Y-%m-%d'),
                'XQH': j,
                'draw': 3,
                'length': 1000,
                'order': [{
                    'column': 0,
                    'dir': 'asc',
                    'name': 'XQ',
                }],
                'pageNum': 1,
                'pageSize': 1000,
                'start':0,
            }),
            cookies=cookies,
            headers={
                'Content-Type':'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0',          
            },
        )
        if data.status_code != 200:
            print(f'Server error.{data.status_code}')
            raise SystemError('Failed to get classroom data.')
        ret.extend(json.loads(data.text)['list'])
    return ret

def get_all_classroom_info(cookies, area):
    area = area or ['01', '02', '03', '04', '05', '06', '07', '08']
    ret = []
    for j in area:
        data = httpx.post(
            'https://pcms.sdu.edu.cn/tp_crp/crp/scra/getClassRoomList',
            content = f'{{"XQH":"{j}"}}',
            cookies=cookies,
            headers={
                'Content-Type':'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0',          
            },
        )
        if data.status_code != 200:
            print(f'Server error.{data.status_code}')
            raise SystemError('Failed to get classroom data.')
        ret.extend(json.loads(data.text)['list'])
    return ret


if __name__ == '__main__':
    import getpass
    username = input('username:')
    password = getpass.getpass('password:')
    with open('Fingerprint.txt', 'r', encoding='utf-8') as f:
        platform_info = f.read()
    cookies = pcms_login(username, password, platform_info)
    data = get_classroom_data(cookies)
    with open('classroom.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
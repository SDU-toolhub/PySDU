# SDU SSO login

Many thanks to existing projects including:

- ![uniform login DES in Python](https://github.com/zhangt2333/awesome-SDU-scripts/blob/master/GPA-Spider/uniform_login/uniform_login_des.py)
- ![SDU SSO](https://github.com/Jenway/SDU_login_API)

现在已经能
Current features:

- login to SDU SSO
- get user info
- get lessons from bkzhjx.wh.sdu.edu.cn

## Install

```bash
pdm install
```

or use pip to install:

```bash
pip install -r requirements.txt
```

## Usage

First, it is recommended that the fingerprint json file be edited. You may use a random json whose keys and values are random strings. I am not sure whether a too-simple string can pass the device fingerprint check on SDU pass.

```bash
python ./src/main.py  # get user info
python ./src/bkzhjx_login.py  # get lessons
```

## Some findings

In cookies file we can find a `SERVERID`. Perhaps we can try getting data from all servers at the same time when some of the servers' response is terribly slow.

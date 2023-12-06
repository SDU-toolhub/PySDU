from login import restful_login, get_user_name_and_id


if __name__ == "__main__":
    import getpass
    try:
        name, student_id = get_user_name_and_id(restful_login(input("请输入学号："), getpass.getpass("请输入密码：")))
    except Exception as e:
        print("登录失败，可能是密码错误")
        print(e)
        exit(1)
    print(f"姓名：{name}")
    print(f"学号：{student_id}")
import sublime
import sublime_plugin
import requests
import re
import json
from os.path import split


class SubmitCode(sublime_plugin.TextCommand):

    def __init__(self, argv):
        super(SubmitCode, self).__init__(argv)
        self.headers = {
            "Host": "acm.sjtu.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://acm.sjtu.edu.cn/OnlineJudge/",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def run(self, edit):
        problem = self.get_problem_id()
        code = self.get_code()
        language = self.get_language()
        if not all((problem, code)):
            print("Ops, failed to get the problem id or code.")
            return
        username, password = self.select_account()
        session = self.login(username, password)
        if session:
            print("Login successfully as {user}.".format(user=username))
        status_code, content = self.submit(problem, code, language, session)
        assert status_code == 200, "Failed to submit!"

    def get_problem_id(self):
        file_name = self.view.file_name()
        if not file_name:
            return False
        _, cpp_file = split(file_name)
        problem_id = cpp_file.split(".")[0]
        if len(problem_id) != 4:
            return False
        try:
            problem_id = int(problem_id)
        except:
            return False
        return problem_id

    def get_code(self):
        file_content = self.view.substr(sublime.Region(0, self.view.size()))
        return file_content

    def get_language(self):
        return 0

    def submit(self, problem, code, language, session=None):
        submit_url = "https://acm.sjtu.edu.cn/OnlineJudge/submit"
        data = {
            "problem": problem,
            "code": code,
            "language": language,
        }
        session = session or requests.Session()
        headers = self.headers.copy()
        headers["Referer"] = "https://acm.sjtu.edu.cn/OnlineJudge/submit"
        r = session.post(submit_url, data, headers=headers)
        return r.status_code, r.content.decode("utf8")

    def login(self, username, password):
        login_data = {
            "action": "登录",
            "password": password,
            "username": username,
        }
        login_url = "https://acm.sjtu.edu.cn/OnlineJudge/login"
        session = requests.Session()
        login_request = session.post(login_url, login_data, headers=self.headers)
        return session if self.check_login(session) == username else None

    def check_login(self, session):
        home_url = "https://acm.sjtu.edu.cn/OnlineJudge/"
        home_request = session.get(home_url, headers=self.headers)
        assert home_request.status_code == 200, "Failed to get the home page"
        html_content = home_request.content.decode("utf8")
        pattern = r"当前用户：(\w+)\W{0,}<"
        match_result = re.findall(pattern, html_content)
        return match_result[0] if match_result else None

    def select_account(self):
        # To-DO: pop up a msgbox to select the account
        # But now, just return an account at random
        try:
            with open("account.json", mode="r", encoding="utf8", errors="ignore") as file:
                account_list = json.load(file)
        except Exception as e:
            print("Failed to load the account file.")
            raise e
        account_num = len(account_list)
        assert account_num != 0, "There's no account in the file!"
        import random
        return account_list[random.randint(0, account_num-1)]

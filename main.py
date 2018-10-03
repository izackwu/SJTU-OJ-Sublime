import sublime
import sublime_plugin
import requests
import re
from os.path import split


class SubmitCode(sublime_plugin.TextCommand):

    def run(self, edit):
        problem = self.get_problem_id()
        code = self.get_code()
        language = self.get_language()
        if not all((problem, code)):
            print("Ops")
            return
        status_code, content = self.submit(problem, code, language)
        print(status_code, content)
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

    def submit(self, problem, code, language):
        submit_url = "https://acm.sjtu.edu.cn/OnlineJudge/submit"
        data = {
            "problem": problem,
            "code": code,
            "language": language,
        }
        headers = {
            "Host": "acm.sjtu.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://acm.sjtu.edu.cn/OnlineJudge/submit",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "216",
            "Cookie": "***",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        r = requests.post(submit_url, data, headers=headers)
        return r.status_code, r.content.decode("utf8")

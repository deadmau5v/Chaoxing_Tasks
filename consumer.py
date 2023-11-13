"""
消费者
"""
from urllib import parse

import jinja2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

import requests

from api import login
from api import course
import encod
from api.claases import Course

mail_host = "smtp.qq.com"
mail_user = "deadmau5v@qq.com"
mail_pass = "mgomnhlyhricefif"

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
template = env.get_template("mail.html")


def send_mail(username: str, password: str, mail: str, mail_title="学习通作业通知") -> bool:
    """发送邮件"""
    token = f"{username}|{password}"
    token = encod.encode(token)
    token = parse.quote(token)
    session = requests.Session()
    login.login(session, username, password)
    courses = course.get_all_task(session)
    for i in courses:
        i: Course = i
        i.tasks = list(filter(lambda x: x.status != "截止未交", i.tasks))
        i.tasks = list(filter(lambda x: "未交" in x.status or "重做" in x.status, i.tasks))

    courses = list(filter(lambda x: len(x.tasks) > 0, courses))
    remove_mail_url = "https://x.d5v.cc/api/remove_mail?token=" + token
    # 格式化模板
    content = {"courses": courses,
               "remove_mail_url": remove_mail_url}
    mail_content = template.render(content)
    message = MIMEMultipart()
    message["From"] = Header(mail_user)
    message["To"] = Header(mail)
    message["Subject"] = Header(mail_title)
    message.attach(MIMEText(mail_content, "html", "utf-8"))

    smtp = smtplib.SMTP_SSL(mail_host)
    smtp.login(mail_user, mail_pass)
    smtp.sendmail(mail_user, mail, message.as_string())
    smtp.quit()
    return True


if __name__ == '__main__':
    if send_mail("17774369488", "18229524142a", "3230772301@qq.com"):
        print("发送成功")

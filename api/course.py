import bs4
import requests as req

from . import configs
from .log import info
from .log import error
from .claases import Course
from .claases import Task


def get_course_list(session: req.Session) -> list[Course]:
    info("获取课程列表...")
    url = "https://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&mcode="
    res = session.get(url, headers=configs.headers)

    if res.json()["result"] != 1:
        error(res.json()['msg'])

    courses = []
    for i in res.json()["channelList"]:
        course = Course()
        if "id" not in i.keys():
            continue
        course.cpi = i["cpi"]
        course.key = i["key"]

        course.image = i["content"]["course"]["data"][0]["imageurl"]
        course.url = i["content"]["course"]["data"][0]["courseSquareUrl"]
        course.teacher = i["content"]["course"]["data"][0]["teacherfactor"]
        course.id = i["content"]["course"]["data"][0]["id"]
        course.name = i["content"]["course"]["data"][0]["name"]

        course.studentcount = i["content"]["studentcount"]
        course.isstart = i["content"]["isstart"]
        course.isretire = True if i["content"]["isretire"] == 0 else False
        courses.append(course)
    return courses


def get_task_by_id(session: req.Session, _id: int, key: int, cpi: int) -> list[Task]:
    url = f"https://mooc1-api.chaoxing.com/work/task-list?courseId={_id}&classId={key}&cpi={cpi}"
    res = session.get(url, headers=configs.headers)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    task_lsit_li = soup.find(name="div", attrs={"id": "pushUp"}).find_all(name="li")

    tasks = []
    for i in task_lsit_li:
        task = Task()
        task.name = i.find(name="p").text.strip()
        task.status = i.find_all(name="span")[0].text.strip()
        if "重" in task.status or "未" in task.status:
            if len(i.find_all(name="span")) > 1:
                task.time = i.find_all(name="span")[-1].text.strip()
            task.isover = False
            if "gray.png" in str(i):
                task.status = "截止未交"
                task.isover = True
        tasks.append(task)
    return tasks


def get_all_task(session: req.Session) -> list[Task]:
    courses = get_course_list(session)
    courses = list(filter(lambda x: not x.isretire, courses))

    for i in courses:
        i: Course = i
        _tasks = get_task_by_id(session, i.id, i.key, i.cpi)
        i.tasks = _tasks

    return courses

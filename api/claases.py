from .log import info


class Course:
    def __init__(self) -> None:
        self.cpi: int = -1
        self.key: int = -1  # classId

        self.id: int = -1
        self.name: str = ""
        self.image: str = ""
        self.url: str = ""
        self.teacher: str = ""

        self.studentcount: int = -1
        self.isstart: bool = False
        self.isretire: bool = False

        self.tasks: list[Task] = []

    def print(self) -> None:
        info(f"课程名称: {self.name}")
        info(f"课程封面: {self.image}")
        info(f"课程链接: {self.url}")
        info(f"课程老师: {self.teacher}")
        info(f"课程人数: {self.studentcount}")
        info(f"课程是否开始: {self.isstart}")
        info(f"课程是否退课: {self.isretire}")
        info(f"课程CPI: {self.cpi}")
        info(f"课程KEY: {self.key}")


class Task:
    def __init__(self) -> None:
        self.name: str = ""
        self.time: str = ""
        self.status: str = ""
        self.isover: bool = True

    def print(self):
        info(f"作业名称: {self.name}")
        info(f"作业状态: {self.status} {'✔' if '批阅' in self.status or '完成' in self.status else '❌'}")
        if self.time:
            info(f"作业时间: {self.time}")

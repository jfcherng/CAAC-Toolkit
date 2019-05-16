from pyquery import PyQuery as pq
import cloudscraper
import os
import re
import sqlite3
import time


def loadDb(dbFilepath):
    if not os.path.isfile(dbFilepath):
        raise Exception(f"DB file does not exist: {dbFilepath}")

    # connect to db file
    with sqlite3.connect(dbFilepath) as conn:

        # build universityMap
        cursor = conn.execute(
            """
                SELECT id, name
                FROM universities
            """
        )
        universityMap = {university[0]: university[1] for university in cursor.fetchall()}

        # build departmentMap
        cursor = conn.execute(
            """
                SELECT id, name
                FROM departments
            """
        )

        departmentMap = {department[0]: department[1] for department in cursor.fetchall()}

    return universityMap, departmentMap


def parseWwwComTw(content=""):
    peopleResult = {
        # '准考證號': {
        #     '_name': '考生姓名',
        #     '系所編號1': {
        #         '_name': '國立臺灣大學醫學系(繁星第八類)',
        #         'isDispatched': False,
        #         'applyState': 'primary',
        #     }
        #     ...
        # },
        # ...
    }

    admissionIdRegex = r"\b(\d{8})\b"
    departmentIdRegex = r"_(\d{6,7})_"

    content = content.replace("\r", "").replace("\n", " ")  # sanitization
    personRows = pq(content)("#mainContent table:first > tr")  # get the result html table

    for personRow in personRows.items():
        findAdmissionId = re.search(admissionIdRegex, personRow.text())

        if findAdmissionId is None:
            continue

        admissionId = findAdmissionId.group(1)
        personName = personRow("td:nth-child(4)").text().strip()

        personResult = {admissionId: {"_name": personName}}

        applyTableRows = personRow("td:nth-child(5) table:first > tr")

        for applyTableRow in applyTableRows.items():
            findDepartmentId = re.search(departmentIdRegex, applyTableRow.html())

            if findDepartmentId is None:
                continue

            departmentId = findDepartmentId.group(1)
            departmentName = applyTableRow("td:nth-child(2)").text().strip()
            applyState = applyTableRow("td:nth-child(3)").text().strip()

            personResult[admissionId][departmentId] = {
                "_name": departmentName,
                "isDispatched": "分發錄取" in applyTableRow.html(),
                "applyState": normalizeApplyStateC2E(applyState),
            }

        peopleResult.update(personResult)

    return peopleResult


def normalizeApplyStateC2E(chinese):
    # 正取
    if "正" in chinese:
        order = re.search(r"(\d+)", chinese)
        order = "?" if order is None else order.group(1)
        return f"primary-{order}"
    # 備取
    if "備" in chinese:
        order = re.search(r"(\d+)", chinese)
        order = "?" if order is None else order.group(1)
        return f"spare-{order}"
    # 落榜
    if "落" in chinese:
        return "failed"
    # 未知（無資料）
    return "unknown"


def normalizeApplyStateE2C(english):
    # 正取
    if "primary" in english:
        state = english.split("-")
        if state[1] == "?":
            state[1] = ""
        return f"正{state[1]}"
    # 備取
    if "spare" in english:
        state = english.split("-")
        if state[1] == "?":
            state[1] = ""
        return f"備{state[1]}"
    # 落榜
    if "failed" == english:
        return "落"
    # 尚未放榜
    if "notYet" == english:
        return "未放榜"
    # WTF?
    return "不明"


def batch(iterable, batchSize=1):
    length = len(iterable)
    for idx in range(0, length, batchSize):
        # python will do the boundary check automatically
        yield iterable[idx : idx + batchSize]


def canBeInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def listUnique(theList, clear=False):
    theList = list(set(theList))

    return filter(len, theList) if clear else theList

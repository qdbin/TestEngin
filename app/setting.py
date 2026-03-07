# -*- coding: utf-8 -*-
import json
import os
import threading
from requests import Session
import zipfile
from app.log import DebugLogger, ErrorLogger
from app.config import DATA_PATH, LMConfig
from app.api import LMApi
from app.plan_builder import build_descriptors_from_test_plan, build_descriptor_index
from app.pytest_runner import run_api_plan


class LMSetting(object):
    """
    测试任务设置和管理类

    负责处理测试任务的数据拉取、文件解压、任务分析和线程创建等核心功能。
    该类是测试执行的核心控制器，管理整个测试流程的设置和执行。
    """

    def __init__(self, task):
        self.task = task
        self.data_path = DATA_PATH
        self.config = LMConfig()

    def data_pull(self):
        """
        从远程服务器拉取测试数据文件

        通过任务配置中的下载URL，下载测试数据ZIP文件到本地数据目录。
        如果数据目录不存在会自动创建，下载过程中会记录日志信息。

        Returns:
            str: 下载成功时返回本地文件路径，失败时返回None

        Example:
            setting = LMSetting(task)
            file_path = setting.data_pull()
            if file_path:
                print(f"数据下载成功: {file_path}")
        """
        data_url = self.task["downloadUrl"]  # 获取数据下载URL
        if not os.path.exists(self.data_path):  # 检查数据目录是否存在
            os.makedirs(self.data_path)  # 创建数据目录
        try:
            file = LMApi().download_task_file(data_url)  # 调用API下载文件
        except Exception as e:
            # 记录下载失败的错误日志
            ErrorLogger(
                "数据拉取失败 错误信息: %s 任务id: %s" % (str(e), self.task["taskId"])
            )
            return None
        else:
            # 构建本地文件保存路径
            file_path = os.path.join(self.data_path, str(self.task["taskId"]) + ".zip")
            with open(file_path, "wb+") as f:  # 以二进制写模式打开文件
                for chunk in file.iter_content(chunk_size=1024):  # 分块读取文件内容
                    if chunk:
                        f.write(chunk)  # 写入文件块
            f.close()
            DebugLogger("数据拉取成功 任务id: %s" % self.task["taskId"])
            return file_path

    def file_unzip(self, file_path):
        """
        解压ZIP文件到数据目录

        验证文件是否为有效的ZIP格式，然后解压所有文件到数据目录。
        解压完成后会删除原始ZIP文件以节省磁盘空间。

        Args:
            file_path (str): 要解压的ZIP文件路径
        """
        r = zipfile.is_zipfile(file_path)  # 验证是否为有效的ZIP文件
        if r:
            with zipfile.ZipFile(file_path, "r") as fz:  # 打开ZIP文件
                for file in fz.namelist():  # 遍历ZIP文件中的所有文件
                    fz.extract(file, self.data_path)  # 解压文件到数据目录
        os.remove(file_path)  # 删除原始ZIP文件

    def _build_task_case_meta(self):
        case_meta = {}
        for collection_map in self.task.get("testCollectionList", []):
            collection_id = str(collection_map.get("collectionId"))
            case_meta.setdefault(collection_id, {})
            for case in collection_map.get("testCaseList", []):
                case_id = str(case.get("caseId"))
                case_meta[collection_id][case_id] = {
                    "caseType": case.get("caseType", "API"),
                    "index": int(case.get("index", 1)),
                }
        return case_meta

    def _build_plan_from_task_dir(self, task_dir):
        test_plan = {}
        case_meta = self._build_task_case_meta()
        if not os.path.isdir(task_dir):
            return test_plan
        for collection in sorted(os.listdir(task_dir)):
            collection_dir = os.path.join(task_dir, collection)
            if not os.path.isdir(collection_dir):
                continue
            session = LMSession()
            driver = LMDriver()
            context = dict()
            order_index = 1
            for filename in sorted(os.listdir(collection_dir)):
                if not filename.lower().endswith(".json"):
                    continue
                case_id = os.path.splitext(filename)[0]
                meta = case_meta.get(str(collection), {}).get(str(case_id), {})
                index = int(meta.get("index", order_index))
                case_type = str(meta.get("caseType", "API"))
                test_case = {
                    "driver": driver,
                    "session": session,
                    "context": context,
                    "task_id": self.task["taskId"],
                    "test_type": case_type,
                    "test_class": "class_" + str(collection),
                    "test_case": "case_%s_%s" % (case_id, index),
                    "test_data": os.path.join(collection_dir, filename),
                }
                test_plan.setdefault(str(collection), []).append(test_case)
                order_index += 1
        return test_plan

    def task_analysis(self):
        """
        分析测试任务并生成测试计划

        Example:
            test_plan = {
                "collection1": [test_case1_dict test_case2_dict],
                "collection2": [test_case3_dict,]
            }
        """
        test_plan = {}
        # 处理普通测试任务
        if self.task["taskType"] != "debug":
            file_path = self.data_pull()  # 拉取测试数据
            if file_path is not None:
                self.file_unzip(file_path)  # 解压测试数据
            task_dir = os.path.join(self.data_path, self.task["taskId"])
            test_plan = self._build_plan_from_task_dir(task_dir)
        # 调试任务
        else:
            collection_map = self.task["testCollectionList"][0]  # 获取第一个集合
            collection = collection_map["collectionId"]  # 获取集合ID
            session = LMSession()  # 创建API测试会话
            driver = LMDriver()  # 创建WEB测试驱动器
            context = dict()  # 创建测试上下文
            case_id = str(collection_map["testCaseList"][0]["caseId"])
            collection_dir = os.path.join(
                self.data_path, str(self.task["taskId"]), str(collection)
            )
            if not os.path.exists(collection_dir):
                os.makedirs(collection_dir)
            case_data_path = os.path.join(collection_dir, case_id + ".json")
            with open(case_data_path, "w", encoding="utf-8") as f:
                json.dump(self.task["debugData"], f, ensure_ascii=False)
            # 构建调试用例配置
            test_case = {
                "driver": driver,
                "session": session,
                "context": context,
                "task_id": self.task["taskId"],
                "test_type": collection_map["testCaseList"][0]["caseType"],
                "test_class": "class_" + collection,
                "test_case": "case_%s_%s"
                % (
                    collection_map["testCaseList"][0]["caseId"],
                    collection_map["testCaseList"][0]["index"],
                ),
                "test_data": case_data_path,
            }
            test_plan[collection] = [test_case]  # 添加到测试计划
        return test_plan

    def create_thread(self, plan, queue, current_exec_status):
        """
        创建线程池执行测试计划

        根据任务配置创建多线程执行环境，支持失败用例重跑功能。
        使用线程池管理并发执行，通过队列传递执行状态信息。

        Args:
            plan (dict): 测试计划字典，包含所有要执行的测试用例
            queue (Queue): 用例结果队列，用于传递执行状态和结果
            current_exec_status (Value): 共享变量，标识当前执行状态
        """
        run_time = 2 if self.task.get("reRun") else 1
        task_id = self.task["taskId"]
        queue.put("run_all_start--%s--API" % task_id)

        last_result = []
        test_plan = plan
        for index in range(run_time):
            if index > 0:
                test_plan = self.read_fail_case(plan, last_result)

            default_result = []
            last_result = default_result

            if len(test_plan) == 0:
                queue.put("start_run_index--%s" % index)
                continue

            queue.put("start_run_index--%s" % index)

            shared_by_collection = {}
            for collection_id, case_list in test_plan.items():
                if not case_list:
                    continue
                shared_by_collection[str(collection_id)] = {
                    "session": case_list[0]["session"],
                    "context": case_list[0]["context"],
                }

            descriptors = build_descriptors_from_test_plan(test_plan)
            descriptor_index = build_descriptor_index(descriptors)
            allure_enabled = str(os.getenv("TESTENGIN_ALLURE", "")).lower() in (
                "1",
                "true",
                "on",
            )
            allure_dir = (
                os.path.join(
                    self.data_path, str(task_id), "allure-results", f"run{index + 1}"
                )
                if allure_enabled
                else None
            )
            run_api_plan(
                task_dir=os.path.join(self.data_path, str(task_id)),
                queue=queue,
                shared_by_collection=shared_by_collection,
                run_times=index + 1,
                default_result=default_result,
                descriptors_by_path=descriptor_index,
                allure_enabled=allure_enabled,
                allure_dir=allure_dir,
            )

        queue.put("run_all_stop--%s" % task_id)
        current_exec_status.value = 1

    @staticmethod
    def read_fail_case(test_plan, result):
        """
        从测试结果中筛选出失败的测试用例

        根据测试结果，筛选出状态为失败（1）或错误（2）的测试用例，
        用于重跑功能中只执行失败的用例。

        Args:
            test_plan (dict): 原始测试计划
            result (list): 测试结果列表，包含每个用例的执行状态

        Returns:
            dict: 包含失败用例的新测试计划

        Note:
            状态码说明：
            - 0: 成功
            - 1: 失败
            - 2: 错误
            - 3: 跳过
        """
        new_test_plan = {}  # 初始化新的测试计划

        # 遍历原始测试计划中的所有集合和用例
        for collection, test_case_list in test_plan.items():
            for test in test_case_list:
                # 从测试用例名中解析出用例ID和索引
                case_id = test["test_case"].split("_")[1]  # 提取用例ID
                index = test["test_case"].split("_")[-1]  # 提取用例索引

                # 在结果列表中查找对应的测试结果
                for case in result:
                    # 匹配集合ID、用例ID和索引
                    if (
                        case["collectionId"] == collection
                        and case["caseId"] == case_id
                        and case["index"] == int(index)
                    ):
                        # 如果状态为失败（1）或错误（2），添加到重跑计划中
                        if case["status"] in (1, 2):
                            if collection not in new_test_plan:
                                new_test_plan[collection] = []  # 初始化集合列表
                            new_test_plan[collection].append(test)  # 添加失败用例
                        result.remove(case)  # 从结果列表中移除已处理的用例
                        break
        return new_test_plan


class LMSession(object):
    """
    API测试会话管理类
    """

    def __init__(self):
        self.session = Session()  # 创建HTTP会话对象


class LMDriver(object):
    """
    WEB测试驱动器管理类
    """

    def __init__(self):
        self.driver = None  # 浏览器驱动器对象，初始为空
        self.config = LMConfig()  # 创建配置管理器实例
        self.browser_opt = self.config.browser_opt  # 获取浏览器启动选项
        self.browser_path = self.config.browser_path  # 获取浏览器可执行文件路径

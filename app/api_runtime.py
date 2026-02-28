from __future__ import annotations

"""
API-only Runtime 适配层（解耦 unittest）。

该模块为 core/api 执行链路提供一个最小可用的“测试实例对象”，用于承载：
- 事务(step)定义/日志/耗时/状态更新
- 失败/错误记录（用于最终 case status 判定）
- 控制台输出捕获（便于平台排障展示）

注意：
- 本模块不包含任何平台上传/调度逻辑，只负责执行期数据收集，避免影响平台回传。
"""

import datetime
import io
import os
import time
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid1

from app.config import IMAGE_PATH, LMConfig


@dataclass
class RuntimeErrorRecord:
    """
    单条运行期异常记录。

    该结构用于在执行完成后统一汇总用例状态：
    - AssertionError -> fail
    - 其他异常 -> error
    """

    exc_type: type
    exc_value: BaseException
    exc_tb: Optional[Any]


class ApiRuntime:
    """
    API 执行期 Runtime。

    该对象将被 core/api/testcase.py 作为 `test` 参数注入，用于：
    - defineTrans/debugLog/errorLog 等记录 transactionList
    - recordFailStatus/recordErrorStatus 记录异常并决定 case 状态
    - saveScreenShot 保持与原引擎一致的截图落盘行为（如果业务用到）
    """

    def __init__(
        self,
        *,
        task_id: str,
        collection_id: str,
        case_id: str,
        index: int,
        run_times: int,
        test_data: Union[str, Dict[str, Any]],
        session: Any,
        context: Dict[str, Any],
    ):
        self.task_id = task_id
        self.collection_id = collection_id
        self.case_id = case_id
        self.index = int(index)
        self.run_index = int(run_times)
        self.case_type = "API"
        self.case_name = f"case_{case_id}_{index}"
        self.test_data = test_data
        self.session = session
        self.context = context
        self.trans_list: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime.datetime] = None
        self.stop_time: Optional[datetime.datetime] = None
        self.stdout_buffer = io.StringIO()  # 捕获 print 输出，最终写入 transaction.log
        self._errors: List[RuntimeErrorRecord] = []
        self._success: bool = True
        self.test_case_name: Optional[str] = None
        self.test_case_desc: Optional[str] = None

    def now_ms(self) -> int:
        """返回当前时间戳（毫秒）。"""
        return int(datetime.datetime.now().timestamp() * 1000)

    def start(self) -> None:
        """记录用例开始时间。"""
        self.start_time = datetime.datetime.now()

    def stop(self) -> None:
        """记录用例结束时间。"""
        self.stop_time = datetime.datetime.now()

    def debugLog(self, log_info: str) -> None:
        """向当前 transaction 追加 debug 日志（HTML 行分隔）。"""
        if not self.trans_list:
            return
        current_time = datetime.datetime.now()
        log = "%s - Debug - %s" % (current_time.strftime("%Y-%m-%d %H:%M:%S.%f"), log_info)
        if self.trans_list[-1]["log"] != "":
            log = "<br><br>" + log
        self.trans_list[-1]["log"] = self.trans_list[-1]["log"] + log

    def errorLog(self, log_info: str) -> None:
        """向当前 transaction 追加 error 日志（HTML 行分隔）。"""
        if not self.trans_list:
            return
        current_time = datetime.datetime.now()
        log = "%s - Error - %s" % (current_time.strftime("%Y-%m-%d %H:%M:%S.%f"), log_info)
        if self.trans_list[-1]["log"] != "":
            log = "<br><br>" + log
        self.trans_list[-1]["log"] = self.trans_list[-1]["log"] + log

    def defineTrans(self, id: str, name: str, content: str = "", desc: Optional[str] = None) -> None:
        """
        定义一个新的 transaction（步骤）。

        行为对齐原引擎：
        - 进入新步骤前，会先将 stdout 归档到上一步日志
        - 若上一步 status 仍为空，则默认置为成功(0)
        """
        if self.trans_list:
            self.complete_output()
            if self.trans_list[-1]["status"] == "":
                self.trans_list[-1]["status"] = 0
        trans_dict = {
            "id": id,
            "name": name,
            "content": content,
            "description": desc,
            "log": "",
            "during": 0,
            "status": "",
            "screenShotList": [],
        }
        self.trans_list.append(trans_dict)

    def complete_output(self) -> None:
        """将 stdout_buffer 中的内容写入当前步骤日志，并清空 buffer。"""
        output = self.stdout_buffer.getvalue()
        self.stdout_buffer.truncate(0)
        self.stdout_buffer.seek(0)
        if output:
            self.debugLog("控制台输出:<br> %s" % output.replace("\n", "<br>"))

    def recordTransDuring(self, during: float) -> None:
        """记录当前步骤耗时（毫秒）。"""
        if self.trans_list:
            self.trans_list[-1]["during"] = during

    def updateTransStatus(self, status: int) -> None:
        """更新当前步骤状态：0成功/1失败/2错误/3跳过。"""
        if self.trans_list:
            self.trans_list[-1]["status"] = status

    def recordFailStatus(self, exc_info: Optional[Tuple[type, BaseException, Any]] = None) -> None:
        """记录断言失败：用于最终用例状态判定为 fail(1)。"""
        self._success = False
        if exc_info is None:
            exc_info = (AssertionError, AssertionError("assert failed"), None)
        self._errors.append(RuntimeErrorRecord(exc_info[0], exc_info[1], exc_info[2]))
        if self.trans_list:
            self.trans_list[-1]["status"] = 1
            self.errorLog(str(exc_info[1]))

    def recordErrorStatus(self, exc_info: Optional[Tuple[type, BaseException, Any]] = None) -> None:
        """记录非断言异常：用于最终用例状态判定为 error(2)。"""
        self._success = False
        if exc_info is None:
            exc = RuntimeError("runtime error")
            exc_info = (RuntimeError, exc, None)
        self._errors.append(RuntimeErrorRecord(exc_info[0], exc_info[1], exc_info[2]))
        if self.trans_list:
            self.trans_list[-1]["status"] = 2
            self.errorLog(str(exc_info[1]))
            if str(LMConfig().enable_stderr).lower() == "true":
                tb_e = traceback.TracebackException(exc_info[0], exc_info[1], exc_info[2])
                msg_lines = list(tb_e.format())
                err_msg = "程序错误信息: "
                for msg in msg_lines:
                    err_msg = err_msg + "<br>" + msg
                self.errorLog(str(err_msg))

    def saveScreenShot(self, name: str, screen_shot: bytes) -> None:
        """保存截图到任务目录，并把截图 uuid 记录到当前步骤。"""
        uuid = time.strftime("%Y%m%d") + "_" + str(uuid1())
        task_image_path = os.path.join(IMAGE_PATH, self.task_id)
        try:
            filename = "%s.png" % uuid
            if not os.path.exists(task_image_path):
                os.makedirs(task_image_path)
            file_path = os.path.join(task_image_path, filename)
            with open(file_path, "wb") as f:
                f.write(screen_shot)
        except Exception:
            self.errorLog("Fail: Failed to save screen shot %s" % name)
        else:
            if self.trans_list:
                self.trans_list[-1]["screenShotList"].append(uuid)

    def ensure_default_trans(self) -> None:
        """确保至少存在一个 transaction，避免平台展示 transactionList 为空。"""
        if not self.trans_list:
            self.defineTrans(self.case_id, "未知", "未知")

    def handleResult(self) -> int:
        """
        汇总用例结果并返回 status：
        - 0: success
        - 1: fail(AssertionError)
        - 2: error(other exception)
        """
        self.ensure_default_trans()
        self.complete_output()
        has_error = any(not issubclass(e.exc_type, AssertionError) for e in self._errors)
        has_fail = any(issubclass(e.exc_type, AssertionError) for e in self._errors)
        if self.trans_list and self.trans_list[-1]["status"] == "":
            self.trans_list[-1]["status"] = 0 if not (has_error or has_fail) else (2 if has_error else 1)
        if has_error:
            return 2
        if has_fail:
            return 1
        return 0

    def error_summary(self) -> str:
        """返回最后一个异常的简要信息，用于 pytest 的失败消息。"""
        if not self._errors:
            return ""
        last = self._errors[-1]
        return str(last.exc_value)

#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import json


class SubmitStatus:
    """
    用于返回填报结果
    """

    def __str__(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4,
            ensure_ascii=False,
        )

    def __init__(
        self,
        check_result=None,
        bind_result=None,
        submit_result=None,
        cancel_result=None,
    ):
        self.check_result: dict = check_result
        self.bind_result: dict = bind_result
        self.submit_result: dict = submit_result
        self.cancel_result: dict = cancel_result

    def session_id(self) -> str:
        if self.check_result is None:
            return ""
        return self.check_result["data"]["sessionId"]

    def is_bind_success(self) -> bool:
        if self.bind_result is None:
            return False
        return self.bind_result["status"]

    def bind_message(self) -> str:
        if self.bind_result is None:
            return ""
        return self.bind_result.get("message", "")

    def bind_user_digest(self) -> str:
        """
        获取用户信息摘要,"{学院}-{班级}-{姓名}",可用于校验填报人员是否正确
        """
        if self.bind_result is None or not self.is_bind_success():
            return "绑定失败"
        user_data = self.bind_result["data"]["user"]
        return f"{user_data['college']}-{user_data['className']}-{user_data['name']}"

    def is_submit_success(self) -> bool:
        if self.submit_result is None:
            return False
        return self.submit_result["status"]

    def recap(self):
        """
        简要说明一下填报结果
        """
        if not self.is_bind_success():
            return f"绑定失败: {self.bind_message()}"

        if self.is_submit_success():
            return f"绑定成功: {self.bind_user_digest()}"
        else:
            return f"{self.submit_result['message']}: {self.bind_user_digest()}"

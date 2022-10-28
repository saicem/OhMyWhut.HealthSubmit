#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import logging
import random
import sys

from requests import Session, session
from health.status import SubmitStatus
from health.form import SubmitForm
from health.tools import base642obj, obj2base64

logging.basicConfig(
    format="%(levelname)s: %(asctime)s - %(filename)s:%(module)s[line:%(lineno)d]: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("health_submit.log"),
        logging.StreamHandler(sys.stdout),
    ],
    encoding="utf-8",
)


class HealthSubmitter:
    def __init__(self, form: SubmitForm) -> None:
        if not isinstance(form, SubmitForm):
            raise Exception("错误的类型，参数 form 不是类型 SubmitForm")
        self.form = form
        self.__session: Session = session()
        self.__session.headers.setdefault("User-Agent", self._rand_agent())
        self.__session.headers.setdefault("Encode", "true")
        self.__session.headers.setdefault("content-type", "application/json")
        self.__session.headers.setdefault("Connection", "keep-alive")

    def submit(self) -> SubmitStatus:
        """
        进行健康填报（绑定->填报->解绑）
        """
        result = SubmitStatus()
        result.check_result = self.check_bind()
        result.bind_result = self._bind_user_info()
        # 绑定是否成功
        if result.is_bind_success():
            result.submit_result = self._submit_form()
        else:
            # 该学号已被其它微信绑定 输入信息不符合
            logging.info(f"绑定失败: {result.bind_message()}")
        result.cancel_result = self._cancel_bind()
        return result

    def check_bind(self):
        """
        尝试绑定，并获取 sessionId
        已绑定
        {
            "status": true,
            "code": 0,
            "message": null,
            "data": {
                "bind": false,
                "sessionId": "88888888-8888-8888-8888-888888888888"
            },
            "otherData": {}
        }
        未绑定
        {
            "status": true,
            "code": 0,
            "message": null,
            "data": {
                "bind": false,
                "sessionId": "88888888-8888-8888-8888-888888888888"
            },
            "otherData": {}
        }
        确实没区别
        """
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/checkBind"
        resp = self.__session.post(url=url, data=self.form.login_form)
        logging.info(resp.text)
        data = self.parse_response(resp.json())
        logging.info(data["data"])
        self.__session.cookies.setdefault("JSESSIONID", data["data"]["sessionId"])
        return data

    def _bind_user_info(self) -> dict[str, object]:
        """
        已被绑定
        {
            "status": false,
            "code": 50000,
            "message": "该学号已被其它微信绑定",
            "data": null,
            "otherData": {}
        }
        错误
        {
            "status": false,
            "code": 50000,
            "message": "输入信息不符合",
            "data": null,
            "otherData": {}
        }
        未绑定
        {
            "status": true,
            "code": 0,
            "message": null,
            "data": {
                "user": {
                    "id": 1***,
                    "openId": "",
                    "sn": "0************",
                    "nickName": "青***",
                    "gender": null,
                    "language": null,
                    "city": null,
                    "province": null,
                    "country": null,
                    "avatarUrl": null,
                    "createDate": "2021-88-88T88:88:88",
                    "updateDate": "2021-88-88T88:88:88",
                    "name": "***",
                    "college": "**学院",
                    "className": "机械**",
                    "major": "华尔兹工程",
                    "unionId": null
                }
            },
            "otherData": {}
        }
        """
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/bindUserInfo"
        resp = self.__session.post(url=url, data=self.form.login_form)
        logging.info(resp.text)
        data = self.parse_response(resp.json())
        logging.info(data["data"])
        return data

    def _submit_form(self) -> dict[str, object]:
        """
        提交表单
        {
            "status": true,
            "code": 0,
            "message": null,
            "data": true,
            "otherData": {}
        }
        {
            "status": false,
            "code": 50000,
            "message": "今日已填报",
            "data": null,
            "otherData": {}
        }
        """
        url = "https://zhxg.whut.edu.cn/yqtjwx/./monitorRegister"
        data = obj2base64(
            {
                "diagnosisName": "",
                "relationWithOwn": "",
                "currentAddress": self.form.address,
                "remark": "无",
                "healthInfo": "正常",
                "isDiagnosis": 0,
                "isFever": 0,
                "isInSchool": int(self.form.is_in_school),
                "isLeaveChengdu": int(self.form.is_leave_wuhan),
                "isSymptom": "0",
                "temperature": self._get_random_temperature(),
                "province": self.form.province,
                "city": self.form.city,
                "county": self.form.county,
            }
        )
        resp = self.__session.post(url=url, data=data)
        logging.info(resp.text)
        data = self.parse_response(resp.json())
        logging.info(data["data"])
        return resp.json()

    def _cancel_bind(self) -> dict[str, object]:
        """
        解除绑定
        {
            "status": true,
            "code": 0,
            "message": null,
            "data": "解绑成功",
            "otherData": {}
        }
        {
            "status": false,
            "code": 50000,
            "message": "解绑用户不存在",
            "data": null,
            "otherData": {}
        }
        """
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/cancelBind"
        resp = self.__session.post(url=url)
        logging.info(resp.text)
        data = self.parse_response(resp.json())
        logging.info(data["data"])
        return data

    @staticmethod
    def _rand_agent() -> str:
        return random.choice(
            [
                "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; MI 6 Build/NXTHUAWEI) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 MQQBrowser/9.9 Mobile Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G36 baiduboxapp/0_01.5.2.8_enohpi_6311_046/5.3.9_1C2%8enohPi/1099a/7D4BD508A31C4692ACC31489A6AA6FAA3D5694CC7OCARCEMSHG/1",
                "Mozilla/5.0 (Linux; U; Android 4.4.4; en-us; vivo X5Max Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/1.0.0.100 U3/0.8.0 Mobile Safari/534.30 AliApp(TB/6.5.0) WindVane/8.0.0 1080X1920 GCanvas/1.4.2.21",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Mobile/14C92 baiduboxapp/0_01.5.2.8_enohpi_8022_2421/2.01_2C2%8enohPi/1099a/05D5623EBB692D46C9C9659B23D68FBD5C7FEB228ORMNJBQOHM/1",
                "Mozilla/5.0 (Linux; Android 8.0.0; BKL-AL00 Build/HUAWEIBKL-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 8.0.0)",
                "Mozilla/5.0 (Linux; Android 8.1.0; vivo X20 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 8.1.0)",
                "Mozilla/5.0 (Linux; Android 9; DUK-AL20 Build/HUAWEIDUK-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 9)",
            ]
        )

    @staticmethod
    def _get_random_temperature() -> str:
        """
        获取用于健康填报的温度
        :return: 正常的温度
        """
        return random.choice(["36°C以下", "36.5°C~36.9°C"])

    @staticmethod
    def parse_response(obj: dict) -> dict[str]:
        if obj["data"] is not None:
            obj["data"] = base642obj(obj["data"])
        return obj

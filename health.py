#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import base64
import logging
import sys
import requests
import random
import json

from requests.sessions import Session

logging.basicConfig(
    format="%(levelname)s: %(asctime)s - %(filename)s:%(module)s[line:%(lineno)d]: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("health_submit.log"),
        logging.StreamHandler(sys.stdout)
    ],
    encoding='utf-8'
)


def base642obj(s: str) -> object:
    return json.loads(base64.b64decode(s))


def obj2base64(obj: object) -> bytes:
    return base64.b64encode(json.dumps(obj).encode())


def parse_response(obj: dict) -> dict[str]:
    if obj['data'] is not None:
        obj['data'] = base642obj(obj['data'])
    return obj


class SubmitStatus:
    """
    用于返回填报结果
    """

    def __init__(self, ok: bool, bind_result=None, submit_result=None, cancel_result=None):
        self.ok = ok
        self.bind_result = bind_result
        self.submit_result = submit_result
        self.cancel_result = cancel_result


class HealthSubmitter:
    def __init__(
            self,
            wx_nickname: str,
            sn: str,
            password: str,
            province: str,
            city: str,
            county: str,
            street: str,
            is_in_school: bool,
            is_leave_wuhan: bool,
    ) -> None:
        """
        健康填报
        :param wx_nickname: 名称（微信名称）
        :param sn: 学号
        :param password: 身份证后六位
        :param province: 省
        :param city: 市
        :param county: 县
        :param street: 街道
        :param is_in_school: 是否在校
        :param is_leave_wuhan: 是否离开学校所在地区
        """
        self.__province: str = province
        self.__city: str = city
        self.__county: str = county
        self.__street: str = street
        self.__login_form = obj2base64({"sn": sn, "idCard": password, "nickname": wx_nickname})
        self.__is_in_school: bool = is_in_school
        self.__is_leave_wuhan: bool = is_leave_wuhan
        self.__session: Session = requests.session()
        self.__session.headers.setdefault("User-Agent", self._rand_agent())
        self.__session.headers.setdefault("Encode", "true")
        self.__session.headers.setdefault("content-type", "application/json")
        self.__session.headers.setdefault("Connection", "keep-alive")

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
        resp = self.__session.post(url=url, data=self.__login_form)
        logging.info(resp.text)
        data = parse_response(resp.json())
        logging.info(data['data'])
        self.__session.cookies.setdefault("JSESSIONID", data['data']["sessionId"])
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
        resp = self.__session.post(url=url, data=self.__login_form)
        logging.info(resp.text)
        data = parse_response(resp.json())
        logging.info(data['data'])
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
        address = f'{self.__province}{self.__city}{self.__county}{self.__street}'
        url = "https://zhxg.whut.edu.cn/yqtjwx/./monitorRegister"
        data = obj2base64({
            "diagnosisName": "",
            "relationWithOwn": "",
            "currentAddress": address,
            "remark": "无",
            "healthInfo": "正常",
            "isDiagnosis": 0,
            "isFever": 0,
            "isInSchool": int(self.__is_in_school),
            "isLeaveChengdu": int(self.__is_leave_wuhan),
            "isSymptom": "0",
            "temperature": self._get_random_temperature(),
            "province": self.__province,
            "city": self.__city,
            "county": self.__county,
        })
        resp = self.__session.post(url=url, data=data)
        logging.info(resp.text)
        data = parse_response(resp.json())
        logging.info(data['data'])
        return resp.json()

    # 取消绑定
    # {
    #     "status": true,
    #     "code": 0,
    #     "message": null,
    #     "data": "解绑成功",
    #     "otherData": {}
    # }
    # {
    #     "status": false,
    #     "code": 50000,
    #     "message": "解绑用户不存在",
    #     "data": null,
    #     "otherData": {}
    # }
    def _cancel_bind(self) -> dict[str, object]:
        """
        解除绑定
        """
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/cancelBind"
        resp = self.__session.post(url=url)
        logging.info(resp.text)
        data = parse_response(resp.json())
        logging.info(data['data'])
        return data

    def submit(self) -> SubmitStatus:
        """
        进行健康填报（绑定->填报->解绑）
        """
        self.check_bind()
        bind_result = self._bind_user_info()
        # 绑定是否成功
        if bind_result["status"]:
            submit_result = self._submit_form()
            cancel_result = self._cancel_bind()

            if submit_result["status"]:
                return SubmitStatus(True, bind_result, submit_result, cancel_result)
            else:
                # 今日已填报
                return SubmitStatus(False, bind_result, submit_result, cancel_result)
        else:
            logging.info(f"绑定失败: {bind_result['message']}")
            cancel_result = self._cancel_bind()
            # 该学号已被其它微信绑定 输入信息不符合
            return SubmitStatus(False, bind_result, None, cancel_result)

    @staticmethod
    def _rand_agent() -> str:
        return random.choice([
            "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; MI 6 Build/NXTHUAWEI) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 MQQBrowser/9.9 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G36 baiduboxapp/0_01.5.2.8_enohpi_6311_046/5.3.9_1C2%8enohPi/1099a/7D4BD508A31C4692ACC31489A6AA6FAA3D5694CC7OCARCEMSHG/1",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; en-us; vivo X5Max Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/1.0.0.100 U3/0.8.0 Mobile Safari/534.30 AliApp(TB/6.5.0) WindVane/8.0.0 1080X1920 GCanvas/1.4.2.21",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Mobile/14C92 baiduboxapp/0_01.5.2.8_enohpi_8022_2421/2.01_2C2%8enohPi/1099a/05D5623EBB692D46C9C9659B23D68FBD5C7FEB228ORMNJBQOHM/1",
            "Mozilla/5.0 (Linux; Android 8.0.0; BKL-AL00 Build/HUAWEIBKL-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 8.0.0)",
            "Mozilla/5.0 (Linux; Android 8.1.0; vivo X20 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 8.1.0)",
            "Mozilla/5.0 (Linux; Android 9; DUK-AL20 Build/HUAWEIDUK-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 9)",
        ])

    @staticmethod
    def _get_random_temperature() -> str:
        """
        获取用于健康填报的温度
        :return: 正常的温度
        """
        return random.choice(["36°C以下", "36.5°C~36.9°C"])

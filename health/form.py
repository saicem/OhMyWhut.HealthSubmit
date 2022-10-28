#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from health.tools import obj2base64


class SubmitForm:
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
        健康填报表单
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
        self.province: str = province
        self.city: str = city
        self.county: str = county
        self.street: str = street
        self.login_form = obj2base64({"sn": sn, "idCard": password, "nickname": wx_nickname})
        self.is_in_school: bool = is_in_school
        self.is_leave_wuhan: bool = is_leave_wuhan
        self.address: str = f'{self.province}{self.city}{self.county}{self.street}'

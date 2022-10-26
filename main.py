#!/usr/bin/env python3
# -*-coding:utf-8 -*-

from health import HealthSubmitter

if __name__ == "__main__":

    status = HealthSubmitter(
        wx_nickname="",
        sn="",
        password="",
        province="",
        city="",
        county="",
        street="",
        is_in_school=True,
        is_leave_wuhan=False
    ).submit()

    if not status.ok:
        print("填报失败")

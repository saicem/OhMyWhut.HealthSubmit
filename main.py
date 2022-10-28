#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from health.form import SubmitForm
from health.submitter import HealthSubmitter

if __name__ == "__main__":

    forms: list = [
        SubmitForm(
            wx_nickname="",
            sn="",
            password="",
            province="",
            city="",
            county="",
            street="",
            is_in_school=True,
            is_leave_wuhan=False,
        ),
    ]

    for form in forms:
        status = HealthSubmitter(form).submit()

        print(status.recap())

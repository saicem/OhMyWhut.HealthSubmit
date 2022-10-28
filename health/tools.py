#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import base64
import json


def base642obj(s: str) -> object:
    return json.loads(base64.b64decode(s))


def obj2base64(obj: object) -> bytes:
    return base64.b64encode(json.dumps(obj).encode())

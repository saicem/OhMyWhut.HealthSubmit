# HealthSubmit
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
![GitHub repo size](https://img.shields.io/github/repo-size/saicem/OhMyWhut.HealthSubmit?style=flat-square)

Python 健康填报脚本

[main.py](main.py) 中填写自己的信息，每天运行即可。

可通过定时任务(云函数，windows 任务计划，linux crontab）每日运行

例如 crontab
```shell
0 0 8 * * ? /home/ubuntu/repos/OhMyWhut.HealthSubmit/main.py
```

参数说明见 [health.py](health.py) HealthSubmitter 的参数说明

参数中的位置信息可使用[腾讯坐标拾取器](https://lbs.qq.com/getPoint/)获取

## Warning

填报逻辑为 绑定->填报->解绑，使用脚本前请先解绑微信。

若不幸出现填报出错的情况，请手动解绑，解绑所需的 sessionId 可查阅日志。

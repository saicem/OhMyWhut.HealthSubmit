# HealthSubmit

![GitHub repo size](https://img.shields.io/github/repo-size/saicem/OhMyWhut.HealthSubmit?style=flat-square)

Python 健康填报脚本

[main.py](main.py) 中填写自己的信息，每天运行即可。
可通过定时任务(windows 任务计划，云服务商的云函数，linux crontab）每日运行

参数说明见 [health.py](health.py) HealthSubmitter 的参数说明

参数中的位置信息可使用[腾讯坐标拾取器](https://lbs.qq.com/getPoint/)获取

欢迎 star、fork、pr

## Warning

填报逻辑为 绑定->填报->解绑，使用脚本前请先解绑微信。

若不幸出现填报出错的情况，请手动解绑，解绑所需的 sessionId 可查阅日志。

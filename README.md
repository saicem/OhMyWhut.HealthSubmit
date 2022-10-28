# HealthSubmit

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
![lines](https://img.shields.io/tokei/lines/github/saicem/OhMyWhut.HealthSubmit)
![size](https://img.shields.io/github/repo-size/saicem/OhMyWhut.HealthSubmit)
![issues](https://img.shields.io/github/issues/saicem/OhMyWhut.HealthSubmit)
![closed issues](https://img.shields.io/github/issues-closed/saicem/OhMyWhut.HealthSubmit)

健康填报脚本

[main.py](main.py) 中填写自己的信息，每天运行即可。

可通过定时任务(云函数，windows 任务计划，linux crontab）每日运行

例如每天早上八点进行健康报送可使用 crontab

```shell
0 8 * * * /home/ubuntu/repos/OhMyWhut.HealthSubmit/main.py
```

参数说明见 [form.py](health/form.py) 的参数说明

位置信息可使用[腾讯坐标拾取器](https://lbs.qq.com/getPoint/)获取

## Warning

填报逻辑为 绑定->填报->解绑，使用脚本前请先解绑微信。

若不幸出现填报出错的情况，请手动解绑，解绑所需的 sessionId 可查阅日志。

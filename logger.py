#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename :logger.py
# @Time     :2020/12/28
# @Author   :dolly
# @Desc     :日志封装
import os
import logging
import re
import os.path
from logging.handlers import TimedRotatingFileHandler

currentDir = os.getcwd()
def getLogger():
    filterFilepath = os.path.join(currentDir,'logs')
    if not os.path.exists(filterFilepath):
        os.makedirs(filterFilepath)
    logPath  = filterFilepath
    backupCount = 60  # 默认保存60天日志
    log_name = 'app'
    logger = logging.getLogger(log_name)
    fileName = os.path.join(logPath, log_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s][%(filename)s-line:%(lineno)d][%(levelname)s]%(message)s')
    fh = TimedRotatingFileHandler(filename=fileName, when="midnight", interval=1, backupCount=backupCount)
    fh.setLevel(logging.DEBUG)
    fh.suffix = "%Y-%m-%d.log"

    # extMatch 是编译好正则表达式
    # suffix和extMatch 一定要匹配的上，否则无法删除过期日志
    fh.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    fh.setFormatter(formatter)

    # 输出日志到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    # 将输出对象添加到Logger中
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


if __name__ == '__main__':
    logger = getLogger()
    logger.info('-----------')

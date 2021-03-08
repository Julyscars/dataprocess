#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename :filter.py
# @Time     :2020/12/28
# @Author   :dolly
import os

currentDir = os.getcwd()

config = {
    'sftp': {
        'host': '192.168.157.170',
        'username': 'xxxx',
        'password': 'xxxxxxx',

    },
    'colname': {
        'inputcol': [],
        'outcol': [],
    },
    'path': {
        'remotepath': '/ddd/ddd',
        'datapath': '/ddd/ddd',
        'inputpath': '/dd/ddd',
        'outpath': '',
        'errpath': '',
    },
    'date': {
        'sleepTime': 30,
        'fileExpire': 3,
        'hisfileExpire': 7,
    }
}

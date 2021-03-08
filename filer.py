#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename :filter.py
# @Time     :2020/12/28
# @Author   :dolly
# @Desc     :文件处理过滤器
import pandas as pd
import abc
import os
import json
import datetime
import time
from logger import getLogger
import shutil
import traceback
logger = getLogger()  # loger init

currentDir = os.getcwd()


class AbstractFilter(abc.ABC):
    @abc.abstractmethod
    def set(self, key, dateTime):
        pass

    @abc.abstractmethod
    def clean(self):
        pass


class FileFilter(AbstractFilter):
    def __init__(self, configDict):
        """
        Initialize the filter, initialize the name of the history file, initialize
        the number of days to save the history file, and initialize
        the number of days to extract new files
        :param configDict:
        """

        filterFilepath = os.path.join(currentDir, 'hisFile')
        if not os.path.exists(filterFilepath):
            os.makedirs(filterFilepath)
        self.filterFilePath = filterFilepath
        self.filterFileName = 'filter.json'
        expire = configDict['hisfileExpire']
        newfileExpire = configDict['fileExpire']

        self.expire = expire  # Default retention days
        # Default number of days to process new files
        self.newfile_expire = newfileExpire
        self.filterFileFullName = os.path.join(
            self.filterFilePath, self.filterFileName)
        if os.path.exists(self.filterFileFullName):
            with open(self.filterFileFullName, 'r') as f:
                his = f.read()
            self.filter = json.loads(his)
        else:
            self.filter = dict()

    def set(self, key, dateTime):
        """
        Update history dictionary key
        :param key:
        :param dateTime:
        :return:
        """
        if not dateTime:
            self.filter[key] = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        else:
            self.filter[key] = dateTime

    def clean(self):
        """
        Clean up the key value within the specified number of days
        :return:
        """
        dealline = (
            datetime.datetime.now() -
            datetime.timedelta(
                days=self.expire)).strftime("%Y-%m-%d %H:%M:%S")
        for key in list(self.filter.keys()):
            dateTime = self.filter[key]
            if dateTime < dealline:
                del self.filter[key]
        content = json.dumps(self.filter, indent=4)
        with open(self.filterFileFullName, 'w') as f:
            f.write(content)

    def findAllFile(self, base):
        """
        :param base: file path
        :return: All file paths completed by iteration
        """
        # Get all file paths under the specified path
        newfile = []
        for root, ds, fs in os.walk(base):
            for f in fs:
                if f.endswith('.txt') or f.endswith('out'):
                    fullname = os.path.join(root, f)
                    newfile.append(fullname)
        return newfile

    def mkDir(self, filepath):
        """
        If the directory folder does not exist, create the specified directory folder
        :param filepath:
        :return:
        """
        path = filepath.strip().rstrip("\\").rstrip("/")
        # Determine whether the specified folder exists
        is_exist = os.path.exists(path)
        if not is_exist:
            # Create specified folder
            os.makedirs(path)

    def keepFile(self, path):
        """
        # Get a list of file names to be deleted under the specified path
        :param path:
        :return:
        """
        new_files = [
            i for i in path if (
                datetime.datetime.fromtimestamp(
                    time.time()) -
                datetime.datetime.fromtimestamp(
                    os.stat(i).st_mtime)).days < self.newfile_expire]
        return new_files

    def newFile(self, path):
        """
        Get new file
        :param path:
        :return:
        """

        # Get history file list
        filterSet = set(list(self.filter.keys()))
        # Get all files in the specified path
        newfiles = self.findAllFile(path)
        # Compare historical files and get a list of new files
        newFiles = set(newfiles).difference(filterSet)
        # Keep a list of new files within the specified number of days
        newFiles = self.keepFile(newFiles)
        return newFiles

    def delFile(self, path, day):
        """

        Get a list of file names to be deleted in the specified number of days under the specified path
        :param path:
        :param day:
        :return:
        """
        del_files = [
            i for i in os.listdir(path) if i.endswith('.txt') and (
                datetime.datetime.fromtimestamp(
                    time.time()) -
                datetime.datetime.fromtimestamp(
                    os.stat(
                        os.path.join(
                            path,
                            i)).st_mtime)).days > day]
        # If the list of files to be deleted is true, then delete the list of
        # files to be deleted
        if del_files:
            for file_name in del_files:
                os.remove(os.path.join(path, file_name))
                logger.info('{} had removed......'.format(file_name))
        else:
            logger.info('No file removed......')

    def mvFile(self, docPath, filePath):
        """
        Move the specified file to the specified folder
        :param docPath:
        :param filePath:
        :return:
        """

        # Create folder
        self.mkDir(filePath)
        # Move the specified file to the specified folder
        shutil.move(docPath, filePath)
        self.set(docPath, dateTime=False)
        self.clean()

    def readFile(self, file, inputcol):
        """
        Read the specified file
        :param file:
        :param inputcol:
        :return:
        """
        tmp = []
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    tmp.append(line.replace('\n', ' ').split('|'))
                except BaseException:
                    continue
        df = pd.DataFrame.from_records(tmp, columns=inputcol)
        return df

    def saveFile(self, df, savefilepath, outputcol, file):
        """
        Save the specified file
        :param df:
        :param savefilepath:
        :param outputcol:
        :param file:
        :return:
        """
        df.to_csv(
            savefilepath,
            columns=outputcol,
            sep='|',
            encoding='utf-8',
            index=False)
        self.set(file, dateTime=False)
        self.clean()

    def checkFilechar(self, path):
        """
        Detect the last character of the last line of the file
        :param path:
        :return:
        """
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
            last_line_char = lines[-1][-1]
            return last_line_char

    def compareFile(self, fistFile, secondFile):
        """
        Compare the size of the files, whether the files are the same
        :param fistFile:
        :param secondFile:
        :return:
        """
        fistFilesize = os.path.getsize(fistFile)
        secondFileseze = os.path.getsize(secondFile)
        if fistFilesize == secondFileseze and self.checkFilechar(
                secondFile) == '#':
            return True
        else:
            return False
    def thirdLoad(self):

        for i in range(3):
            try:
                pass

                logger.info('Data processing completed ..')
            except Exception as e:
                logger.error('Data processubg err ..')
                logger.error(traceback.format_exc())


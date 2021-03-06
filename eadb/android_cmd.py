#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Time    : 2018/10/15 18:23
# Author  : gaojiewen
# Version : 1.0
# Desc    : 封装 adb 常用命令


import re
import os
import logging
from eadb.utils import check_is_none, get_time, run_command


class AndroidAdb(object):

    def __init__(self):
        check_adb_is_ok = run_command('adb start-server')
        if 'command not found' in check_adb_is_ok:
            logging.error(r'请添加 ANDROID_HOME 环境变量')
            raise EnvironmentError(r'Please set ANDROID_HOME first.')
        self.ids = self.devices()

    def devices(self):
        """
        获取当前连接的设备
        :return: 设备列表
        """
        devices = []
        output = run_command('adb devices')
        lines = output.split('\n')
        for i in range(1, len(lines)):
            if 'device' in lines[i]:
                devices.append(lines[i].replace('\tdevice', ''))
        logging.info(r'获取到已连接的设备：{0}'.format(devices))
        if check_is_none(devices):
            logging.warning(r'当前无 Android 设备连接')
            return None
        return devices

    def device_info(self, id=None):
        """
        获取指定设备常用信息

        返回字符串格式：
        {
            "abcds": {
                "name": "device1",
                "version": "4.4.2"
            },
            "123dfs": {
                "name": "device2",
                "version": "7.1.1"
            }
        }

        :param id: 设备 id
        :return: 设备相关信息列表
        """
        info_dict = {}
        one_device_info = {}
        one_device_info['platform'] = 'Android'
        one_device_info['name'] = self.device_name(id=id)
        one_device_info['version'] = self.device_version(id=id)
        one_device_info['wm_size'] = self.device_wm_size(id=id)
        info_dict[id] = one_device_info
        return info_dict

    def device_screenshot(self, id=None):
        """
        对指定设备进行截屏，并放到电脑的桌面上
        :param id: 设备号
        """
        device_name = self.device_name(id)
        version = self.device_version(id)
        screen_file = '{0}-{1}-{2}.png'.format(device_name, version, get_time())
        screen_path = '{0}/Desktop/{1}'.format(os.environ['HOME'], screen_file)
        logging.info(r'截图存放路径：{0}'.format(screen_path))
        screen_in_device = '/sdcard/{0}'.format(screen_file)
        run_command('adb -s {0} shell screencap {1}'.format(id, screen_in_device))
        run_command('adb -s {0} pull {1} {2}'.format(id, screen_in_device, screen_path))
        run_command('adb -s {0} shell rm {1}'.format(id, screen_in_device))
        print(r"'{0}'截屏成功，存放路径为'{1}'".format(device_name, screen_path))

    def device_name(self, id=None):
        """
        获取指定设备的名称

        返回字符串格式：
        {
            "01e5169b322": "google-Nexus_5X"
        }

        :param id: 设备 id
        :return: 设备名称
        """
        name = ''
        model = run_command('adb -s {0} shell getprop ro.product.model'.format(id)).replace(' ', '_')
        model = re.sub('\r\n|\n', '', model)
        brand = run_command('adb -s {0} shell getprop ro.product.brand'.format(id))
        brand = re.sub('\r\n|\n', '', brand)
        # 找到字符串返回0，找不到返回-1
        if model.find(brand) == 0:
            name = model.replace('_', '-')
        else:
            name = '{0}-{1}'.format(brand, model)
        logging.info(r"获取到设备'{0}'的名称：'{1}'".format(id, name))
        return name

    def device_version(self, id=None):
        """
        获取指定设备的系统版本

        返回字符串格式：
        {
            "010799de5169b322": "7.1.1"
        }

        :param id: 设备 id
        :return: 系统版本
        """
        version = ''
        version_or = run_command('adb -s {0} shell getprop ro.build.version.release'.format(id))
        version = re.sub('\r\n|\n', '', version_or)
        logging.info(r"获取到设备'{0}'的系统版本号为'{1}'".format(id, version))
        return version

    def device_wm_size(self, id=None):
        """
        获取指定设备的屏幕大小

        返回字符串格式：
        {
            "010799de5169b322": "1080x1920"
        }

        :param id: 设备号
        :return: 设备大小
        """
        size = ''
        size = run_command('adb -s {0} shell wm size'.format(id))
        size = size.split(':')[1].strip()
        size = re.sub('\r\n|\n', '', size)
        logging.info(r"获取到设备'{0}'的屏幕大小为'{1}'".format(id, size))
        return size


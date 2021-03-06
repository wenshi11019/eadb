#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Time    : 2019-02-25 11:29
# Author  : gaojiewen
# Version : 1.0
# Desc    : 


import re
import os
import logging
from eadb.utils import check_is_none, get_time, run_command


class IOSCmd(object):

    def __init__(self):
        check_ios_is_ok = run_command('idevice_id -l')
        if 'command not found' in check_ios_is_ok:
            logging.error(r'请安装 iOS 开发环境.')
            raise EnvironmentError(r'Please install iOS development environment first.')
        self.ids = self.devices()

    def devices(self):
        """
        获取当前连接的设备
        :return: 设备列表
        """
        devices = []
        output = run_command('idevice_id -l')
        # 先判断有没有设备连接
        if check_is_none(output):
            logging.warning(r'当前无 iOS 设备连接')
            return None
        origin_list = output.split('\n')
        for d in origin_list:
            if not check_is_none(d):
                devices.append(d)
        logging.info(r'获取到已连接的设备：{0}'.format(devices))
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
        one_device_info['platform'] = 'iOS'
        one_device_info['name'] = self.device_name(id=id)
        one_device_info['version'] = self.device_version(id=id)
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
        screen_log = run_command('idevicescreenshot -u {0} {1}'.format(id, screen_path))
        if not check_is_none(screen_log) and 'Could not start screenshotr service' in screen_log:
            print(r'iOS 截屏服务出错，请修复')
            logging.error(screen_log)
            exit(1)
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
        model = run_command('idevicename -u {0}'.format(id)).replace(' ', '_')
        model = re.sub('\r\n|\n', '', model)
        name = model
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
        product_version = run_command('ideviceinfo -u {0} | grep "ProductVersion"'.format(id))
        version = product_version.split(':')[1].strip()
        version[id] = re.sub('\r\n|\n', '', version)
        logging.info(r"获取到设备'{0}'的系统版本号为'{1}'".format(id, version))
        return version

    def device_wm_size(self, id=None):
        # 目前考虑已机型判断分辨率
        print("ios 不支持")
        pass

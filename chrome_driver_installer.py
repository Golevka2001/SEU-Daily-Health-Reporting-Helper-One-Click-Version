'''Automatically install correct chrome driver.
@Author: Gol3vka<gol3vka@163.com>
@Created date: 2022/10/15
@Last modified date: 2022/10/17
'''

import requests
import re
import os
import time
import winreg

#from webdriver_manager.core.utils import get_browser_version_from_os
from webdriver_manager.chrome import ChromeDriverManager

# site to download:
download_url = 'https://chromedriver.storage.googleapis.com'

# get chrome path from registry:
try:
    path_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r'SOFTWARE\\Clients\\StartMenuInternet\\Google Chrome\\DefaultIcon')
except Exception:
    print(
        '[ERROR]Can not find chrome installed in your system, please download manually'
    )
    time.sleep(1)
    os.system('start https://www.google.cn/chrome/')  # download page of chrome
    exit(-1)
browser_path = winreg.QueryValueEx(path_key, '')[0].split(',')[0]
driver_path = os.path.join(os.path.dirname(browser_path), 'chromedriver.exe')

# get chrome version from registry:
try:
    version_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'SOFTWARE\\Google\\Chrome\\BLBeacon')
    browser_version = winreg.QueryValueEx(version_key, 'version')[0]
except Exception:
    print('[ERROR]Can not get chrome version, please enter here')
    browser_version = input('version = ')
browser_version_split = browser_version.split('.')
if len(browser_version_split) < 4:
    print('[ERROR]Incorrect format, example: 106.0.5249.119')
    exit(-1)

# this is another method to get chrome version, using webdriver_manager:
'''
if (browser_version := get_browser_version_from_os('google-chrome')) is None:
    print('[ERROR]Can not get chrome version, please enter here')
    browser_version = input('version = ')
else:
    browser_version = browser_version + '.0'
browser_version_split = browser_version.split('.')
if len(browser_version_split) < 4:
    print('[ERROR]Incorrect format, example: 106.0.5249.119')
    exit(-1)
'''

# get response from the site:
response = requests.get(url=download_url)
content = response.text

# search for matched version:
for i in reversed(range(4)):
    rule = f'<Contents><Key>({browser_version_split[0]}\.{browser_version_split[1]}\.{browser_version_split[2]}\.{browser_version_split[3]})/chromedriver_win32\.zip</Key>.*?'
    if (search_result := re.search(rule, content, re.S)) is not None:
        driver_version = search_result.group(1)
        break
    elif i == 0:
        raise Exception(
            '[ERROR]Can not find matched version, please download manually, current browser version: ' +
            browser_version)
        time.sleep(1)
        os.system('start https://registry.npmmirror.com/binary.html?path=chromedriver/')  # download page of chrome driver
        exit(-1)
    else:
        browser_version_split[i] = '\d+'

download_path = ChromeDriverManager(version=driver_version,
                                    path=os.path.abspath(
                                        os.path.dirname(__file__))).install()
# copy chromedriver to chrome folder:
print('[INFO]Copying chromedriver.exe...')
os.system('copy \"%s\" \"%s\"' % (download_path, driver_path))
print('[INFO]Chrome driver path: %s' % driver_path)

# delete useless download files:
print('[INFO]Please confirm to delete temp files')
os.system('rmdir .\\.wdm\\ /s')

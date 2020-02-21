import os
import re
import time
from os.path import join, getsize
import datetime
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException, NoSuchFrameException, \
    TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import win32con
import win32gui
from selenium.webdriver import Chrome

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import ProtocolError


def getdirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def start_dl(file_folder_name):
    print("csdn会员下载器启动准备中...")
    root_path = os.getcwd()
    print("开始创建下载目录...")
    download_path = root_path + "\\" + file_folder_name
    print(download_path)
    if not os.path.exists(download_path):
        os.mkdir(file_folder_name)
        print("目录创建成功，目录名为：" + file_folder_name + "，物理路径为：" + download_path)
    else:
        print("目录已存在，目录名为：" + file_folder_name + "，物理路径为：" + download_path)
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_path,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True,
             "profile.managed_default_content_settings.images": 2  # 无图模式
             }
    # 将自定义设置添加到Chrome配置对象实例中
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--headless')  # 游览器无头模式
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chromedriver_path = root_path + "\\Google Chrome x86\\chromedriver.exe"
    end_wait_flag = 0  # 等待驱动窗口隐藏标志位
    print("连接chromedriver中...")
    browser = Chrome(chrome_options=chrome_options,
                     executable_path='./Google Chrome x86/chromedriver.exe')
    cd = win32gui.FindWindow(None, chromedriver_path)
    # print(cd)
    while cd == 0:
        if end_wait_flag == 3:
            return None  # 出错停止运行，返回None
        time.sleep(1)
        end_wait_flag += 1
        cd = win32gui.FindWindow(None, chromedriver_path)
        print(cd)
    win32gui.ShowWindow(cd, win32con.SW_HIDE)
    print("连接chromedriver成功！！！")
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
    browser.execute("send_command", params)
    print("csdn会员下载器准备就绪...")
    return browser


def download(download_url, file_folder_name, browser):
    login_url = "https://graph.qq.com/oauth2.0/show?which=Login&display=pc&client_id=100270989&response_type=code" \
                "&redirect_uri" \
                "=https%3A%2F%2Fpassport.csdn.net%2Faccount%2Flogin%3FpcAuthType%3Dqq%26state%3Dtest "
    browser.get(login_url)
    print("开始登录csdn...")
    browser.switch_to.frame('ptlogin_iframe')
    browser.find_element_by_id("switcher_plogin").click()
    print("登录csdn中...")
    browser.find_element_by_id("u").clear()
    browser.find_element_by_id("u").send_keys("1093616634")
    browser.find_element_by_id("p").clear()
    browser.find_element_by_id("p").send_keys("17190310515hzk")
    browser.find_element_by_id('login_button').click()
    print("登录成功！！！")
    print("正在跳转下载地址...")
    WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "login_img")))
    browser.get(download_url)
    print("跳转成功！！！")
    file_size = browser.find_element_by_class_name("size_box").text
    file_size = str(file_size).split("：")[1].split("MB")[0]  # 简单粗暴，提取大小
    print("获取文件大小，大小：" + file_size + "MB")
    WebDriverWait(browser, 10, 1).until(EC.presence_of_element_located((By.LINK_TEXT, "VIP下载")))
    down_a = browser.find_element_by_link_text("VIP下载")
    down_a.click()
    print("正在获取下载链接...")
    WebDriverWait(browser, 5, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, "pop_close")))
    vip_a_list = browser.find_elements_by_link_text("VIP下载")
    vip_a_list[1].click()
    file_size = float(file_size)
    print("开始下载，预计下载时间{}s左右".format(int(file_size)))
    print("正在下载中......")
    dirpath = './' + file_folder_name + '/'
    su1 = 0
    for i in range(1, 3600):
        time.sleep(0.9)
        print('\r' + "开始下载,耗时{}s".format(i), end="")
        sz = getdirsize(dirpath) / 1024 / 1024
        su2 = sz - su1
        su1 = sz
        print(",实时网速：{:.2f}KB/s".format(su2 * 1024), end="")
        if file_size - sz <= 0.01:
            break
    print(",下载成功！！！")
    print()
    print("稍等3~5秒，关闭进程，否则电脑会卡顿...")
    print()
    time.sleep(2)
    return browser


try:
    print()
    print('"使用说明！！！！！！"')
    print()
    print('"url.txt"文件中填写正确的下载网址，并放置一行中，程序只读一行！')
    print('注意：本程序必须和"url.txt"文件放在同一文件夹中，否则程序无法正常运行！')
    print('注意：本程序必须和"Google Chrome x86"文件夹放在同一文件夹中，否则程序无法正常运行！')
    print('注意：不要乱动"Google Chrome x86"文件夹中的配好的文件！这会导致程序无法正常运行！')
    print('千万注意：使用本程序时不要挂网络代理软件上网,这会导致文件下载失败！')
    print()
    print()
    print()
    print("开始！")
    time.sleep(1)
    print("读取下载网址...")
    fr = open("./url.txt", encoding="utf-8")
    download_url = fr.readline()
    fr.close()
    download_url = download_url.replace(" ", "")
    print(download_url)
    # download_url = "https://download.csdn.net/download/qq_41479464/12156567"
    searchObj = re.search(r'https://download.csdn.net/download/(.*)/(.*)', download_url, re.M | re.I)
    if searchObj:
        print("验证网址正确！！！")
        file_folder_name = searchObj.group(1) + searchObj.group(2) + datetime.datetime.now().strftime('%H-%M-%S')
        browser = start_dl(file_folder_name)
        browser = download(download_url, file_folder_name, browser)
        cmd = os.popen('taskkill /f /t /im chromedriver.exe')
        time.sleep(1.5)
        browser.quit()
        fr = cmd.read()
        print(fr)
    else:
        print("不是正确的csdn资源网址！！！")
        exit(0)
except FileNotFoundError:
    print('"url.txt"不在指定位置，请将"url.txt"文件和本程序放在同一文件夹中！')
except NoSuchFrameException:
    print('软件功能失效，请联系开发者！')
except NoSuchElementException:
    print('软件功能失效，请联系开发者！')
except TimeoutException:
    print('软件功能失效，请联系开发者！')
except ProtocolError:
    print('远程主机强迫关闭了一个现有的连接！')
except SessionNotCreatedException:
    print('会话异常终止！请确认软件正常运行中...')
except AttributeError:
    print("启动失败，请检查chromedriver.exe！！！(chromedriver需和chrome游览器版本相对应)")
except WebDriverException:
    print('启动chromedriver失败！请确认"chromedriver.exe"在"Google Chrome x86"文件夹中')
finally:
    print("请手动关闭此窗口，默认不会自动关闭！")
    print("如果遇到错误，try again gain ain！")
    print("重新尝试多次未果！请联系开发者")

time.sleep(3600)
print()

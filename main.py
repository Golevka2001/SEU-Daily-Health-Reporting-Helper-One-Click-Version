'''Automatically report health condition for SEUers.
@What's new: now you can add more SEUers to the config file,\
    and this script will be executed for all users in the list on one click.
    No need to schedule a list of tasks!
@Author: XAKK
@Forked by: Gol3vka<gol3vka@163.com>
@Created date: 2020/12/25 - XAKK
@Last modified date: 2022/10/30 - Gol3vka
'''

from email_sending_module import EmailSendingModule

import os
import time
from random import random

import requests
import yaml
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class ReportingHelper:

    def __init__(self):
        # absolute path:
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   'config.yml')

        if not os.path.exists(config_path):
            raise Exception('[ERROR]No such file of directory: ' + config_path)
        else:
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config = yaml.safe_load(config_file.read())
                config_file.close()

            class Config:
                chrome_driver_path = config.get('chrome_driver_path')  # str
                user_id = config.get('user_id')  # list
                password = config.get('password')  # list
                notification = config.get('notification')  # list
                notify_failure_only = config.get('notify_failure_only')  # list
                to_addr = config.get('to_addr')  # list
                from_addr = config.get('from_addr')  # str
                email_password = config.get('email_password')  # str
                smtp_server = config.get('smtp_server')  # str
                port = config.get('port')  # int

            self.cfg = Config

    def check_connection(self) -> None:
        '''Check the Internet connection, pause when no connection
        '''
        while True:
            try:
                requests.get("https://www.seu.edu.cn", timeout=2)
                break
            except Exception:
                print('[ERROR]Please check the Internet connection.')
                input('>>> Press ENTER To Retry <<<')

    def generate_random_temperature(self) -> str:
        '''Generate random normal body temperature: [36.2, 36.7]

        Returns:
            str: normal body temperature
        '''
        lower_bound = 36.2
        x = random() / 2  # [0, 0.5]
        return str(round(lower_bound + x,
                         1))  # round to one decimal place: 36._

    def run(self):
        # judgement for item number of the lists in settings:
        user_count = len(self.cfg.user_id)
        if not (user_count == len(self.cfg.password) == len(
                self.cfg.notification) == len(self.cfg.notify_failure_only) ==
                len(self.cfg.to_addr)):
            raise Exception(
                '[ERROR]Please check the config file, all lists should have the same number of items.'
            )

        options = Options()
        options.add_argument('--headless')  # headless browser
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')

        # loop for different users in the list:
        for i in range(user_count):
            driver = Chrome(service=Service(self.cfg.chrome_driver_path),
                            options=options)

            driver.get(
                'http://ehall.seu.edu.cn/appShow?appId=5821102911870447')
            driver.find_element(By.ID, 'username').send_keys(
                self.cfg.user_id[i])  # student ID
            driver.find_element(By.ID, 'password').send_keys(
                self.cfg.password[i])  # password
            driver.find_element(
                By.XPATH,
                '//*[@class="auth_login_btn primary full_width"]').click()

            temperature = self.generate_random_temperature()
            status = ''
            try:
                WebDriverWait(driver, 15, 0.2).until(lambda x: x.find_element(
                    By.XPATH, '//*[@class="bh-btn bh-btn-primary"]'))
                driver.find_element(
                    By.XPATH, '//*[@class="bh-btn bh-btn-primary"]').click()
                WebDriverWait(driver, 15, 0.2).until(
                    lambda x: x.find_element(By.NAME, 'DZ_JSDTCJTW'))
                driver.find_element(By.NAME,
                                    'DZ_JSDTCJTW').send_keys(temperature)
                driver.find_element(By.ID, 'save').click()
                WebDriverWait(driver, 15, 0.2).until(lambda x: x.find_element(
                    By.XPATH,
                    '//*[@class="bh-dialog-btn bh-bg-primary bh-color-primary-5"]'
                ))
                driver.find_element(
                    By.XPATH,
                    '//*[@class="bh-dialog-btn bh-bg-primary bh-color-primary-5"]'
                ).click()
                status = 'successful' + '\ntemperature:' + str(temperature)
            except Exception as e:
                status = 'failed'
                print(str(e))

            # send an e-mail to notify result:
            if self.cfg.notification[i] == 'yes':
                self.email = EmailSendingModule()
                sender_information = {
                    'address': self.cfg.from_addr,
                    'password': self.cfg.email_password,
                    'alias': 'Daily Health Reporter'
                }
                receivers_information = {'address': self.cfg.to_addr[i]}
                server_information = {
                    'address': self.cfg.smtp_server,
                    'port': self.cfg.port
                }

                if self.cfg.notify_failure_only[i] == 'no':
                    mail = {'subject': '[NOTIFICATION]', 'body': status}
                    self.email.config.load_from_parameters(
                        sender_information, receivers_information, mail,
                        server_information)
                    result = self.email.send_emails()
                    if result[1] == 0:
                        print('[INFO]Successful sending')
                    else:
                        print('[INFO]Failed sending')
                elif status == 'failed':
                    mail = {'subject': '[NOTIFICATION]', 'body': status}
                    self.email.config.load_from_parameters(
                        sender_information, receivers_information, mail,
                        server_information)
                    result = self.email.send_emails()
                    if result[1] == 0:
                        print('[INFO]Successful sending')
                    else:
                        print('[INFO]Failed sending')

            driver.close()
            print(
                '[INFO]' +
                time.strftime('%Y-%m-%d %H:%M:%S -', time.localtime()), status)


if __name__ == '__main__':
    print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S -', time.localtime()),
          'start')
    rh = ReportingHelper()
    rh.check_connection()
    rh.run()

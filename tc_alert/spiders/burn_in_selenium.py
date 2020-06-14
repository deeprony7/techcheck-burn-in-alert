# -*- coding: utf-8 -*-
import json, os, smtplib
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail(message, title):
        print("Sending mail...........")     
        gmailUser = os.getenv('W_EMAIL')
        gmailPassword = os.getenv('W_PASS')
        recipient = os.getenv('W_EMAIL')    #   multiple recipients = 'xyz@smartshifttech.com,xxxxxx@smartshifttech.com'
        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['To'] = recipient
        msg['Subject'] = title
        msg.attach(MIMEText(message))
        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient.split(',') , msg.as_string())  #   multiple recipients
        mailServer.close()
        print("Mail sent")

class CoinSpiderSelenium(scrapy.Spider):
    name = 'burn_in_selenium'
    allowed_domains = ['www.techcheck.cengage.com']
    start_urls = [
        'https://techcheck.cengage.com/login'
    ]

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_path = '/home/shouvick/PycharmProjects/untitled/scrapy-projects/livecoin/chromedriver'

        driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
        driver.set_window_size(1920,5080)
        driver.get("https://techcheck.cengage.com/login")
        driver.implicitly_wait(15)
        username = driver.find_element_by_css_selector("#username-field")
        username.click()
        username.send_keys("shalder")
        passwd = driver.find_element_by_css_selector("#password-field")
        passwd.click()
        passwd.send_keys(f"{os.getenv('TC_PASS')}")
        passwd.send_keys(Keys.RETURN)
        driver.implicitly_wait(10)
        driver.get("https://techcheck.cengage.com")
        driver.implicitly_wait(20)

        self.html = driver.page_source
        # driver.close()

    def parse(self, response):
        response = Selector(text=self.html)
        # read old data to compare state
        # with open('record_state.json', 'r') as fp:
        #     old_state = json.load(fp)
        dict = {}
        for platform in response.xpath("//div[@class='MuiPaper-root MuiCard-root SplashPage_system_18pPS SplashPage_internal_1RvCv MuiPaper-elevation1 MuiPaper-rounded']"):
            dict.update({platform.xpath(".//a/div/div[2]/p/text()").get():platform.xpath(".//div/div[1]/div[1]/text()").get()}) 
        print(dict)
        # write new data
        with open("record_state.json", "w") as write_data:
                    json.dump(dict, write_data)
        
        platforms_monitored = ['Diet & Wellness Plus Health Check', 'ANZ HE Commerce - SOLR Service', 'ANZ HE Commerce - Your Cart', 'Jira [only affects internal users]', 'eCommerce US - Search and Add to Cart (new 2020)']

        # for platform in platforms_monitored:
        #     if (old_state[platform] != dict[platform]):
        #         msg = f"{platform} platform status changed to {dict[platform]}"
        #         send_mail(msg, msg)

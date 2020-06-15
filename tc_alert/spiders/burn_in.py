'''
Idea is to use scrapy splash to render the javascript page "https://techcheck.cengage.com/" and parse platform status for the burn-in systems. If there is a change of platform state then program will send out an email to team's group DL.
1. render
2. parse
3. email
'''
# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
import smtplib
import json
import os
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

class BurnInSpider(scrapy.Spider):
    name = 'burn_in'
    allowed_domains = ['www.techcheck.cengage.com']
    # perhaps modify to send_keys("<ENTER>") after entering password?
    script = f'''
        function main(splash, args)
            splash:on_request(function(request)
              request:set_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36')
            end)
            splash.private_mode_enabled = false
            url = args.url
            assert(splash:go(args.url))
            assert(splash:wait(6))
            username = assert(splash:select("#username-field"))
            username:focus()
            username:send_text("shalder")
            assert(splash:wait(0.5))
            passwd = assert(splash:select("#password-field"))
            passwd:focus()
            passwd:send_text("{os.getenv('TC_PASS')}")
            assert(splash:wait(0.5))
            btn = assert(splash:select("#login-btn > span.MuiButton-label"))    
            btn:mouse_click()
            assert(splash:wait(1))
            home = assert(splash:select("#home-btn > span.MuiIconButton-label > span"))
            home:mouse_click()
            assert(splash:wait(2))
            expand = assert(splash:select("#expand-all-btn > span.MuiButton-label"))
            expand:mouse_click()
            assert(splash:wait(1))
            splash:set_viewport_full()
            return {{
                html = splash:html()
                }}
            end
    '''

    def start_requests(self):
        yield SplashRequest(url="https://techcheck.cengage.com/login", callback=self.parse, endpoint='execute', args={
            'lua_source': self.script
        })
    

    def parse(self, response):
        # read old data to compare state
        with open('record_state.json', 'r') as fp:
            old_state = json.load(fp)
        dict = {}
        for platform in response.xpath("//div[@class='MuiPaper-root MuiCard-root SplashPage_system_18pPS SplashPage_internal_1RvCv MuiPaper-elevation1 MuiPaper-rounded']"):
            dict.update({platform.xpath(".//a/div/div[2]/p/text()").get():platform.xpath(".//div/div[1]/div[1]/text()").get()})  
        # write new data
        with open("record_state.json", "w") as write_data:
                    json.dump(dict, write_data)
        
        platforms_monitored = ['Diet & Wellness Plus Health Check', 'ANZ HE Commerce - Search and Add to Cart', 'ANZ HE Commerce - SOLR Service', 'ANZ HE Commerce - Your Cart', 'Jira [only affects internal users]', 'eCommerce US - Search and Add to Cart (new 2020)']

        for platform in platforms_monitored:
            if (old_state[platform] != dict[platform]):
                msg = f"{platform} platform status changed to {dict[platform]}"
                send_mail(msg, msg)
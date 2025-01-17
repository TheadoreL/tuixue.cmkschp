#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2021/6/20 7:00 PM
# @Author    :Eason Tang
import sys

from helper import request_sail_ticket, create_assist_date
from bark_helper import bark_push
import time
import smtplib
import email.mime.multipart
import email.mime.text
import requests

# ==================================
# Global Settings
# Github Action
enable_gh_action = False  # 启用GitHub Action
# Bark Push
enable_bark = False  # 启用Bark推送
bark_token = ""  # Bark推送ID
# SMTP config
enable_mail = False  # 启用邮件推送
smtp_url = ""
smtp_port = 25
smtp_from_address = ""
smtp_to_address = ""
smtp_password = ""
# MailGun config
enable_mail_gun = False   # 启用MailGun推送
mailgun_domain_name = ""
mailgun_api_key = ""
mailgun_to_address = ""

# Ticket Stuff
startSite = "SK"  # 始发站点
endSite = "HKA"  # 目标站点
startDate = "2021-09-14"  # 船票搜索日期
endDate = "2021-09-14"
show_available_only = True  # 只显示有票的日期
# ==================================

def sendMail(mailContent):
    smtp = smtplib
    smtp = smtplib.SMTP()
    smtp.connect(smtp_url, smtp_port)
    smtp.login(smtp_from_address, smtp_password)
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = smtp_from_address
    msg['subject'] = '船票Get'
    msg['to'] = smtp_to_address
    txt=email.mime.text.MIMEText(mailContent,'HTML','utf-8')
    msg.attach(txt)
    smtp.sendmail(msg['from'],msg['to'],str(msg))

def mailGun(mailContent):
    return requests.post(
        "https://api.mailgun.net/v3/"+ mailgun_domain_name +"/messages",
        auth=('api', mailgun_api_key),
        data={"from": "船票Get <mailmaster@"+ mailgun_domain_name +">",
              "to": [mailgun_to_address],
              "subject": "船票Get",
              "text": mailContent})

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--action":
        enable_gh_action = True  # 检测是否在GitHub Action中运行

    toDate = create_assist_date(datestart=startDate, dateend=endDate)  # 船票的起止时间

    while True:
        for date in toDate:
            ret = request_sail_ticket(request_param={
                "startSite": startSite,  # 蛇口港
                "endSite": endSite,  # 香港机场
                "toDate": date  # 乘船日期
            },
                show_available_only=show_available_only)
            if ret is not None and ret != -1:
                print(f'{date}:{ret}')
                if enable_mail:
                    sendMail(f'{date}:{ret}')
                if enable_mail_gun:
                    mailGun(f'{date}:{ret}')
                if enable_bark:
                    bark_push(token=bark_token, title="船票Get", content=ret)
            elif ret == -1:
                print(f'{date}:爬取失败')
            else:
                print(f'{date}:没有可用的船票')

        if enable_gh_action:
            break
        time.sleep(600)
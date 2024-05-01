import json
import os
import time
import requests
import configparser
from bs4 import BeautifulSoup as bs
import ddddocr

# don't use this account


class Bot:
    def __init__(self, info):

        self.s = requests.session()
        self.baseurl = "https://cpe.cse.nsysu.edu.tw/cpe/"

        self.ocr = ddddocr.DdddOcr()

        self.soup = bs("lxml")

        self.logined = False
        self.succeed = False

        self.acc = info[0]
        self.pwd = info[1]
        self.token = info[2]

    def login(self):
        res = self.s.get(self.baseurl)
        self.soup = bs(res.text, "html.parser")
        imgPath = self.soup.find("img")['src']
        captcha = self.getCaptcha(imgPath)
        payload = {
            'isFirst': 'no',
            'myLevel': 'on',
            'id': self.acc,
            'pw': self.pwd,
            'captcha': captcha,
        }
        res2 = self.s.post(self.baseurl, data=payload)
        with open("test.html","w",encoding=res2.encoding) as f:
            f.write(res2.text)

        if 'logout' in res2.text:
            self.logined = True
            self.Consolelog("{} {}".format("Login Success",captcha))
        elif '驗證碼輸入錯誤' in res2.text:
            self.Consolelog("{} {}".format("Captcha Failed 驗證碼輸入錯誤",captcha))
            self.login()
        else:
            self.Consolelog("Login Failed")

    def getCaptcha(self, imgPath):
        r = self.s.get(self.baseurl + imgPath, stream=True)

        if r.status_code == 200:
            with open('cap.jpg', 'wb') as f:
                for chunk in r:
                    f.write(chunk)

        with open('cap.jpg', 'rb') as f:
            image_bytes = f.read()

        captcha = self.ocr.classification(image_bytes)
        return captcha

    def Consolelog(self, msg):
        temp = "{} {} ".format(time.strftime(
            "[%Y-%m-%d %H:%M:%S]", time.localtime()), msg)
        print(temp)
        

    def LineNotifyLog(self, msg):
        headers ={
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/x-www-form-urlencoded"}
        temp = "{} {} ".format(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), msg)

        params = {"message": temp}
        requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)

    def SignUp(self):
        payload = {
            'isSend': 'yes',
            'mySchoolID': 21,
            'myDepartment': '資訊工程學系',
            'myGrade': 111,
            'optionsRadios': 1,
            'site': 66,  # yzu : 66
            'yesExam': '報名',
        }

        try:
            res = self.s.post(self.baseurl+"newest", data=payload)
        except:
            self.Consolelog("handle exception")
            self.login()
            return

        if '您已報名本次 CPE 測驗' in res.text:
            self.Consolelog("您已報名本次 CPE 測驗")
            self.succeed = True
        elif '已報名' in res.text:
            self.Consolelog("Signin Success")
            self.succeed = True
        elif '報名失敗：該考場人數已額滿' in res.text:
            self.Consolelog("該考場人數已額滿")
        elif '非報名時間' in res.text:
            self.Consolelog("非報名時間")
        else:
            self.Consolelog("Unhandled Failed SignIn")
            self.login()  # try to handle Failure


if __name__ == "__main__":
    configFilename = 'private.ini'
    if not os.path.isfile(configFilename):
        with open(configFilename, 'a') as f:
            f.writelines(["[Default]\n", "acc= your account\n",
                         "pwd= your password\n", "token= your LineNotifyToken\n"])
            exit()

    config = configparser.ConfigParser()
    config.read(configFilename)

    info = [config['Default']['acc'], config['Default']['pwd'],
                config['Default']['token']]

    myBot = Bot(info)
    myBot.login()
    print("1234")
    while not myBot.succeed:
        myBot.SignUp()
        time.sleep(3)

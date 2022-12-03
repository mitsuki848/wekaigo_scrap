import os
import re
import shutil
import zipfile
from pip._vendor import requests
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from bs4 import BeautifulSoup

# from webdriver_manager.core.utils import get_browser_version_from_os
# print(get_browser_version_from_os(browser_type='google-chrome'))

#実行環境上のChromeブラウザのバージョン
current_version = ""

webdriver_url   = "https://chromedriver.storage.googleapis.com/" #ウェブドライバーページ
file_name       = "chromedriver_win32.zip" #Windows用のファイル名
driver = webdriver.Chrome(executable_path=os.getcwd() + ".wdm\drivers\chromedriver\win32\chromedriver.exe")

# ChromeWebdriverファイルのパス指定
try:
    if os.path.isfile(os.getcwd() + "\\webdriver\\chromedriver.exe")== False:
        raise FileNotFoundError()

    driver = webdriver.Chrome(executable_path=os.getcwd() + "\\webdriver\\chromedriver.exe")
    driver.close()
except (FileNotFoundError,SessionNotCreatedException) as e:
    if type(e) == SessionNotCreatedException:
        print("WebDriverファイルが古い可能性があります。最新バージョンのダウンロードを開始開始します。")
        tmp = re.split("\n",str(e)) #例外メッセージを改行で区切る
        tmp = re.split(" ",tmp[1])# 右記のようなメッセージを半角スペースで区切る（Current browser version is 96.0.4664.110 with binary path WebDriverパス）
        tmp = re.split("\.",tmp[4]) #バージョン情報ドットで区切る
        current_version = tmp[0]+"."+tmp[1]+"."+tmp[2]
    elif type(e)==FileNotFoundError:
        print("WebDriverファイルが存在しません。ダウンロードを開始開始します。")
    else:
        print("不明な例外です。")
        print(e)
        exit()

    response = requests.get(webdriver_url)
    soup = BeautifulSoup(response.text,"lxml-xml")#lxmlのインストールが必要

    if not os.path.exists(os.getcwd() + "\\webdriver\\tmp\\"):
        os.makedirs(os.getcwd() + "\\webdriver\\tmp\\")

    success_flg = False
    for version in reversed(soup.find_all("Key")):
        if((current_version != "" and version.text.startswith(current_version))
        or (current_version == "" and version.text.endswith(file_name))):
            get_version = re.sub("/.*","",version.text)
            zip_source = requests.get(webdriver_url + get_version + "/" + file_name)
            print("起動テストを開始します\t"+webdriver_url + get_version + "/" + file_name)

            # ダウンロードしたZIPファイルの書き出し
            with open(os.getcwd() + "\\webdriver\\tmp\\" + file_name, "wb") as file:
                for chunk in zip_source.iter_content():
                    file.write(chunk)

            # ZIPファイルの解凍
            with zipfile.ZipFile(os.getcwd() + "\\webdriver\\tmp\\" + file_name) as file:
                file.extractall(os.getcwd() + "\\webdriver\\tmp\\")

            try:
                driver = webdriver.Chrome(executable_path=os.getcwd() + "\\webdriver\\tmp\\chromedriver.exe")
                if(os.path.isfile(os.getcwd() + "\\webdriver\\chromedriver.exe")):
                    os.remove(os.getcwd() + "\\webdriver\\chromedriver.exe")
                shutil.move(os.getcwd() + "\\webdriver\\tmp\\chromedriver.exe",os.getcwd() + "\\webdriver\\chromedriver.exe")

                print("正常に起動しました。WebDriverを上書きします。")

                shutil.rmtree(os.getcwd() + "\\webdriver\\tmp\\")
                success_flg = True
                break
            except SessionNotCreatedException as e:
                print("起動中にエラーが発生しました。\t"+webdriver_url + get_version + "/" + file_name)
    if not success_flg:
        print("WebDriverファイルの上書き中に例外が発生しました。処理を中断します")


print("WebDriverの処理を記述。。。")

#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pyautogui as pg
import os
import time
import pywinauto as pwa
import PySimpleGUI as sg
import schedule
import sched
import time
import datetime
import calendar
import random
import glob
import threading
import sys
from pathlib import Path
import webbrowser

class Zoom():
    def __init__(self):
        #日付日時関連
        self.week_id = 2
        self.year_id = 2022
        self.hour_id = 16
        self.minute_id = 10

        # パス関連
        self.defoult_zoom_url = "XXX"
        self.path0 = "path0.png"
        self.path1 = "path1.png"
        self.path2 = "path2.png"

        # グローバル変数関連
        self.recode = 0

    def enter_zoom(self):
        # zoomのURLに遷移
        print("入室")
        webbrowser.open(zoom_url, new=2)
        time.sleep(3)
        while True:
            try:
                p1=pg.locateOnScreen(self.path1, confidence=0.8)
                x1, y1 = pg.center(p1)
                pg.move(x1, y1)
                pg.click(x1, y1)

                time.sleep(3)
                x2, y2 = pg.center(p2)
                pg.move(x2, y2)
                pg.click(x2, y2)
                break
            except:
                p0=pg.locateOnScreen(self.path0, confidence=0.8)
                x0, y0 = pg.center(p0)
                pg.move(x0, y0)
                pg.click(x0, y0)
                continue
            

    def exit_zoom(self):
        print("退室")
        # Zoom Client閉じる
        zoom = pwa.Application(backend="uia").connect(best_match=u"Zoom ミーティング")
        if zoom[u"Zoom ミーティング"].exists():
            zoom[u"Zoom ミーティング"].set_focus()
            pwa.keyboard.send_keys("%{F4}") # zoomのウィンドウを閉じる (Alt+F4)
            pwa.keyboard.send_keys("{ENTER}")

    def capture_zoom(self):
        print("録画中")
        if button:
            self.recode = 1
        zoom = pwa.Application(backend="uia").connect(best_match=u"Zoom ミーティング")
        zoom[u"Zoom ミーティング"].set_focus() # 録画対象
        pwa.keyboard.send_keys("{VK_LWIN down}%{R down}{VK_LWIN up}{R up}") # 録画開始(Win+Alt+R)
        #time.sleep(10)
        #pwa.keyboard.send_keys("{VK_LWIN down}%{R down}{VK_LWIN up}{R up}") # 録画終了(Win+Alt+R)

    def get_today(self):
        dt_now = datetime.datetime.now()
        dt_now = datetime.datetime(dt_now.year, dt_now.month, dt_now.day, dt_now.hour, dt_now.minute, 0)
        print("dt_now", dt_now)
        
        # 今日の曜日取得(水曜日=2)
        week_id = calendar.weekday(dt_now.year, dt_now.month, dt_now.day)
        
        now_time = int(time.mktime(dt_now.utctimetuple()))
        print(now_time)
        
        return dt_now, week_id, now_time
    
    def pre_processing_time(self):
        dt_now, week_id, now_time = self.get_today()
        enter_time = '{}-{}-{} {}:{}:00'.format(dt_now.year, dt_now.month, dt_now.day, enter_h, enter_m)
        enter_time = datetime.datetime.strptime(enter_time, '%Y-%m-%d %H:%M:%S')
        enter_time = int(time.mktime(enter_time.utctimetuple()))
        print("enter_time", enter_time)

        exit_time = '{}-{}-{} {}:{}:00'.format(dt_now.year, dt_now.month, dt_now.day, exit_h, exit_m)
        exit_time = datetime.datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
        exit_time = int(time.mktime(exit_time.utctimetuple()))
        print("exit_time", exit_time)

        return enter_time, exit_time

    ###UIで取り込む###
    # レイアウト
    def make_app(self):
        global enter_h, enter_m, exit_h, exit_m, zoom_url, zoom_pass, button
        L1=[[sg.Text("入室時間")],\
        [sg.InputText(default_text="16",size=(10,1), key="enter_h",text_color="#000000"),
        sg.Text("時"),
        sg.InputText(default_text="10",size=(10,1), key="enter_m",text_color="#000000"),
        sg.Text("分")],\
        [sg.Text("退室時間")],\
        [sg.InputText(default_text="17",size=(10,1), key="exit_h",text_color="#000000"),
        sg.Text("時"),
        sg.InputText(default_text="50",size=(10,1), key="exit_m",text_color="#000000"),
        sg.Text("分")]]
        L2=[[sg.Text("URL")],\
        [sg.InputText(default_text=self.defoult_zoom_url, size=(60,1), key="zoom_url",text_color="#000000")],\
        [sg.Text("パスワード(あれば)")],\
        [sg.InputText(size=(60,1),key="zoom_pass",text_color="#000000")]]
        L=[[sg.Frame("ミーティング時刻",L1)],\
        [sg.Frame("ZoomのURL",L2)],\
        [sg.Checkbox("授業を録画する",default=False,pad=((0, 380),(0, 0))),
        sg.Button("実行",font=("", 13)),
        sg.Button("終了",font=("",13))]]
        # ウィンドウ作成
        window = sg.Window("Zoom自動入退室の設定", L)
        # イベントループ
        counter=0
        while True:
            event , values = window.read() # イベントの読み取り（イベント待ち）
            if event == "実行":
                enter_h=values["enter_h"]
                enter_m=values["enter_m"]
                exit_h=values["exit_h"]
                exit_m=values["exit_m"]
                zoom_url=values["zoom_url"]
                tx6=values["zoom_pass"]
                button=values[0]
                self.startEvent(event)

            #print("イベント:",event ,",値:",values) # 確認表示
            
            if (event == None) or (event =="終了") : # 終了条件（ None: クローズボタン）
                self.finishEvent(event,window)
            
    #並列化開始        
    def start(self):
        global thread
        thread = threading.Thread(target = self.main)
        thread.setDaemon(True)
        thread.start()

    
    #スタートボタン押下時の処理
    def startEvent(self, event):
        self.start()
    

    # 終了ボタン押下処理     
    def finishEvent(self, event, window):
        if self.recode==1:
            pwa.keyboard.send_keys("{VK_LWIN down}%{R down}{VK_LWIN up}{R up}") #録画終了
        window.close()#ウインドウを消す
        sys.exit() #アプリ終了

    def main(self):
        print("入室時間",enter_h,"時",enter_m, "分")
        print("退室時間",exit_h,"時" ,exit_m, "分")
        enter_time, exit_time = self.pre_processing_time() 
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enterabs(enter_time, 1, self.enter_zoom)
        if button:
            scheduler.enterabs(enter_time, 2, self.capture_zoom)
        scheduler.enterabs(exit_time, 1, self.exit_zoom)
        scheduler.run()

if __name__ == '__main__':
    z = Zoom()
    z.make_app()
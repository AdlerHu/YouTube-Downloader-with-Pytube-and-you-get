import tkinter as tk
import ytubeX_modules as m
from tkinter import messagebox
from pytube import YouTube
import threading
import re

def click_func():
    # 取得文字輸入框的網址
    url = yt_url.get()
    # 如果是空字串就結束函式
    if url.strip() == "" : return

    # 進行爬蟲，看是否是播放清單
    urls = m.get_urls(url)
    if urls:
        if messagebox.askyesno('確認方塊',
                               '是否下載清單內所有影片？(選擇 否(N) 則下載單一影片)'):
            threading.Thread(target=multi_dload,  # ←下載清單中所有影片
                             args=(urls, listbox)).start()
        else:
            threading.Thread(target=m.start_dload,  # ←下載單一影片
                             args=(url, listbox)).start()
    else:  # ←沒有播放清單, 直接下載
        threading.Thread(target=m.start_dload,
                         args=(url, listbox)).start()


def multi_dload(urls,listbox):
    # 設定執行續上限
    max_thread = threading.activeCount() +20
    urls.sort(key = lambda s:int(re.search("index=\d+",s).group()[6:]))

    # 用迴圈建立和啟動執行續
    for url in urls:
        # 執行續到達上限就等待
        while threading.activeCount() >= max_thread:
            pass
        threading.Thread(target=m.start_dload,
                         args=(url, listbox)).start()


window = tk.Tk()
listbox,yt_url = m.build_window(window,click_func)
window.mainloop()
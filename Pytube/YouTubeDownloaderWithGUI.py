import tkinter as tk
import ytube_modules as m
from tkinter import messagebox
from pytube import YouTube
import threading


def click_func():
    url = yt_url.get()
    try:
        YouTube(url)
    except:
        messagebox.showerror("錯誤","pytube不支援此影片或者網址錯誤")
        return

    # pytube 支援這個網址，進行爬蟲
    urls = m.get_urls(url)

    # 輸入網址中有影片清單
    if urls and messagebox.askyesno('確認方塊',
                                    '是否下載清單內所有影片？(選擇 否(N) 則下載單一影片)'):

        # 下載清單中所有影片
        print("開始下載清單")
        for u in urls:
            threading.Thread(target=m.start_dload,args=(u,listbox)).start()
    else:
        yt = YouTube(url)
        if messagebox.askyesno("確認方塊",
                               f'是否下載{yt.title}影片?'):
            threading.Thread(target=m.start_dload,
                             args=(url,listbox)).start()
        else:
            print("取消下載")


window = tk.Tk()
listbox,yt_url = m.build_window(window,click_func)

window.mainloop()
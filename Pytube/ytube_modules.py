from bs4 import BeautifulSoup
import requests
import threading
from pytube import YouTube
import tkinter as tk

lock = threading.Lock()


def start_dload(url,listbox):
    yt = YouTube(url)

    name = yt.title

    lock.acquire()
    no = listbox.size()
    listbox.insert(tk.END,f'{no:02d}:{name}.....下載中')
    print("插入:",no,name)
    lock.release()

    yt.streams.first().download()

    lock.acquire()
    print("更新:",no,name)
    listbox.delete(no)
    listbox.insert(no,f'{no:02d}:●{name} 下載完成....')
    lock.release()


def get_urls(url):
    urls = []   # 影片清單網址
    if '&list=' not in url : return urls    # 單一影片
    response = requests.get(url)    # 發送 GET 請求
    if response.status_code != 200:
        print('請求失敗')
        return
    # -----↓ 請求成功 ↓------ #
    bs = BeautifulSoup(response.text, 'lxml')
    a_list = bs.find_all('a')
    base = 'https://www.youtube.com/'        # Youtube 開頭網址
    for a in a_list:
        href = a.get('href')
        url = base + href
        if ('&index=' in url) and (url not in urls):
            urls.append(url)
    return urls


def build_window(window,click_func):
    window.geometry("640x480")
    window.title("YouTube極速下載器")

    # ----------Frame:上方輸入網址區域----------
    input_fm = tk.Frame(window, bg="red", width=640, height=120)
    input_fm.pack()

    # ----------Label---------
    lb = tk.Label(input_fm, text="請輸入YouTube影片網址", bg="red", fg="white", font=("細明體", 12))
    lb.place(rely=0.25, relx=0.5, anchor="center")

    # ----------Entry----------
    yt_url = tk.StringVar()
    entry = tk.Entry(input_fm, textvariable=yt_url, width=50)
    entry.place(rely=0.5, relx=0.5, anchor="center")

    btn = tk.Button(input_fm, text="下載影片", command=click_func, bg="#FFD700", fg="Black", font=("細明體", 10))
    btn.place(rely=0.5, relx=0.85, anchor="center")

    # ----------Frame:下方顯示下載清單區域
    dload_fm = tk.Frame(window, width=640, height=480 - 120)
    dload_fm.pack()

    # ----------Label----------
    lb = tk.Label(dload_fm, text="下載狀態", fg="black", font=("細明體", 10))
    lb.place(rely=0.1, relx=0.5, anchor="center")

    # ----------Listbox----------
    listbox = tk.Listbox(dload_fm, width=65, height=15)
    listbox.place(rely=0.5, relx=0.5, anchor="center")

    # ----------Scrollbar----------
    sbar = tk.Scrollbar(dload_fm)
    sbar.place(rely=0.5, relx=0.87, anchor="center", relheight=0.7)

    # List與Scrollbar的連結
    listbox.config(yscrollcommand=sbar.set)
    sbar.config(command=listbox.yview)
    return listbox, yt_url
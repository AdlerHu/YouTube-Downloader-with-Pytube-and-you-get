from bs4 import BeautifulSoup
import requests
import threading
from pytube import YouTube
import tkinter as tk
import subprocess as sp

lock = threading.Lock()


def start_dload(url,listbox):
    no = set_listbox(listbox,-1,f'讀取 {url}')
    # 先使用you-get讀取資訊
    title, best = yget_info(url)
    # 若you-get無法讀取,改用pytube讀取
    if title == "":
        try:
            yt = YouTube(url)
            title=yt.title + "*"
            # 設為空字串表示可用pytube下載
            best = ""
        # Pytube也讀取失敗
        except:
            pass
    # 更新listbox
    if title == "":
        name = "影片無法讀取"
    else:
        name = f'{title}...下載中'

    # 更新listbox中第no項的內容
    set_listbox(listbox,no,name)
    # 開始下載，若無法讀取影片資訊就return
    if title == "":
        return
    # best不是空字串就表示可以用you-get下載
    if best:
        yget_dl(url)
    # 使用pytube下載
    else:
        yt.streams.first().download()

    set_listbox(listbox,no,f'{title}...下載完成')



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


# you-get 查詢影片資訊的函式
def yget_info(url):
    process = sp.Popen("you-get -i " + url,
                       shell=True,
                       stdout=sp.PIPE,stderr=sp.PIPE)
    r = process.communicate()
    s = str(r[0],"utf-8")
    print(s)

    # 搜不到title:則視為失敗
    if s.find("title:") < 0:
        return "", ""

    # 觀察用you-get -i 指令查詢影片的結果，發現title會在title:和streams之間，取出後再用strip()去除空白
    title = s[s.find("title:") + 6: s.find("streams")].strip()
    itag = s[s.find("itag:")+6: s.find("container")].strip()

    # 如果 itag0 內容有 ESC 資料(例 b'\x1b[7m137\x1b[0m'),去除、前後4個 ESC 字元
    if len(itag) > 8:
        itag = itag[4:-4]

    # 傳回title為空字串時表示讀取失敗
    return title, itag


# you-get下載影片的函式
def yget_dl(url,itag=None):
    cmd = "you-get "
    if itag:
        cmd = cmd + "--itag=" + itag + " "
    process = sp.Popen(cmd+url)
    process.wait()
    # 傳回0表示OK
    return process.returncode


# 建立視窗的函式
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

    return listbox,yt_url


def set_listbox(listbox,pos,msg):
    lock.acquire()
    if pos < 0:
        pos = listbox.size()
        listbox.insert(tk.END,f'{pos+1:02d}:' + msg)
    else:
        listbox.delete(pos)
        listbox.insert(pos,f'{pos+1:02d}:' +msg)
    lock.release()
    return pos
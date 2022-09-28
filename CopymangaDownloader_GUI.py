#By Animuses
from encodings import utf_8
import os
import json
from tkinter import messagebox
from tkinter.ttk import Combobox, Progressbar
import requests
from urllib import parse
import re
from Crypto.Cipher import AES
import binascii
import threading
from tkinter import *

window = Tk()
dispurl = StringVar()
dispurl.set('copymanga.site')
mainurl = dispurl.get()
validate = '未检测'

#窗口属性初始化
def init_window():
    window.title("CopymangaDownloader_GUI")
    window.geometry('868x681+100+100')
    window.rowconfigure(0,weight=1)
    window.rowconfigure(1,weight=1)
    window.rowconfigure(2,weight=1)
    window.rowconfigure(3,weight=1)
    window.rowconfigure(4,weight=1)
    window.columnconfigure(0,weight=1)
    window.columnconfigure(1,weight=1)
    window.columnconfigure(2,weight=1)
    window.columnconfigure(3,weight=1)
    window.columnconfigure(4,weight=1)
    window.minsize(400,200)

#联网检测函数
def grab(mainurl):
    #当前有效网址
    global validate
    try:
        requests.get(f'https://{mainurl}')
    except requests.exceptions.ConnectionError:
        validate = '无效！在此可输入新网址'
    else:
        validate = '有效！'
     
#错误后检测
def check1():
    check_urllabel.grid_remove()
    check()

#联网检测按键处理
def check():
    mainurl = dispurl.get()
    grab(mainurl)
    global check_urllabel
    check_urllabel = Label(check_frame,text=f'当前网址：{mainurl}，该网址{validate}')
    check_urllabel.grid(row=0,column=0,padx=5,pady=5)
    if validate == '无效！在此可输入新网址':
        check_frame.pack(expand='true')
    elif validate == '有效！':
        checknext_button = Button(check_frame, text="下一步", bg="lightblue", width=8,command=search)
        checknext_button.grid(row=2, column=0,padx=5,pady=5)

#跳转搜索
def search():
    check_frame.pack_forget()
    search_frame.pack(expand='true')

#搜索函数
def search_start():
    global pathwordlist,manganamelist,mangaaliaslist,mangaauthorlist
    search_frame.pack_forget()
    search_result_frame.pack(padx=5,pady=5)
    searchname=parse.quote(searchdispname.get())
    searchurl = f'https://{mainurl}/api/kb/web/searchs/comics?offset=0&platform=2&limit=12&q={searchname}'
    searchreq = requests.get(searchurl)
    searchjson  = searchreq.json()
    resultlist = searchjson['results']['list']
    scounter = 1
    pathwordlist = [0]
    manganamelist = [0]
    mangaaliaslist = [0]
    mangaauthorlist = [0]
    for results in resultlist:
        resultname = results['name']
        resultalias = results['alias']
        resultauthorlist = results['author']
        pathwords = results['path_word']
        for resultauthors in resultauthorlist:
            resultauthor = resultauthors['name']
            break
        listdisplay = f'{resultname}'
        pathwordlist.insert(scounter,pathwords)
        manganamelist.insert(scounter,resultname)
        mangaaliaslist.insert(scounter,resultalias)
        mangaauthorlist.insert(scounter,resultauthor)
        result_search_list.insert(scounter,listdisplay)
        scounter = scounter + 1
        
def searchdetail():
    global selector
    selector = result_search_list.curselection()[0]+1
    selectname = manganamelist[selector]
    selectalias = mangaaliaslist[selector]
    selectauthor = mangaauthorlist[selector]
    result_detail_label = Text(search_result_frame,width=30,height=40)
    result_detail_label.insert(END,f'漫画名称：\n{selectname}\n\n又名：\n{selectalias}\n\n作者：\n{selectauthor}')
    result_detail_label.config(state="disabled")
    result_detail_label.grid(row=2, column=2,padx=5,pady=5)
    detail_button = Button(search_result_frame, text="确定", bg="lightblue", width=5,command=chapterwindow)
    detail_button.grid(row=3, column=2,padx=5,pady=5)

def chapterwindow():
    search_result_frame.pack_forget()
    chapter_frame.pack(padx=5,pady=5)
    chapter_fetch()

def chapter_fetch():
    global manganame,pathword,uuidlist,namelist
    manganame = manganamelist[selector]
    pathword = parse.quote(pathwordlist[selector])
    chapter_list.insert(END,f'已选择：{manganame}\n')
    #拉取加密章节列表
    cipherurl = f'https://{mainurl}/comicdetail/{pathword}/chapters'
    cipherreq = requests.get(cipherurl)
    cipherjson = cipherreq.json()
    listcipher = cipherjson['results']
    #解密
    key = 'xxxmanga.woo.key'.encode('utf_8')
    iv = listcipher[:16].encode('utf_8')
    cipher = binascii.a2b_hex(listcipher[16:])
    mode = AES.MODE_CBC
    aes = AES.new(key, mode, iv)
    cplistb = aes.decrypt(cipher)
    cplist = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]',"",cplistb.decode('utf-8'))
    #处理章节列表并显示
    listjson = json.loads(cplist)
    groups = listjson['groups']
    groupnum = 1
    cpnum = 1
    namelist = [0]
    uuidlist = [0]
    selectlist = []
    for grouplist in groups:
        groupname = groups[grouplist]['name']
        chapter_list.insert(END,f'\n{groupnum}：{groupname}')
        groupnum = groupnum + 1

        for chapterlist in groups[grouplist]['chapters']:
            chaptername = chapterlist.get('name')
            chapteruuid = parse.quote(chapterlist['id'])
            namelist.insert(cpnum,chaptername)
            uuidlist.insert(cpnum,chapteruuid)
            chapter_list.insert(END,f'\n--{cpnum}：{namelist[cpnum]}')
            selectlist.insert(cpnum,f'\n--{cpnum}：{namelist[cpnum]}')
            cpnum = cpnum + 1
    chapter_list.grid(row=1,column=1)
    chapter_list.config(state="disabled")
    chapter_selector['value']=selectlist
    chapter_selector1['value']=selectlist

#下载
def downloadwindow():
    dlchoices = int(re.search('--(\d+)：',chapter_selector.get()).group(1))
    dlchoicee = int(re.search('--(\d+)：',chapter_selector1.get()).group(1))
    if dlchoicee>=dlchoices:
        chapter_frame.pack_forget()
        download_frame.pack()
        if os.path.isdir(f"./{manganame}"):
            pass
        else:
            os.mkdir(f"./{manganame}")
        i = 0
        for i in range(dlchoices,dlchoicee + 1):
            threading.Thread(target = download , args = (i,)).start()
        else:
            pass
            #download_log.config(state="disabled")
    else:
        messagebox.showerror('错误','下载范围错误，请检查下载起始章节不应大于结束章节')

def download(num):
    download_log.insert(END,f'即将下载：{namelist[num]}\n')
    counter = 1
    filename = str(counter).zfill(4)
    cpurl = f'https://api.{mainurl}/api/v3/comic/{pathword}/chapter/{uuidlist[num]}'
    reqget = requests.get(cpurl)
    getjson = reqget.json()
    jsonfilter=getjson['results']['chapter']['contents']
    lenth = len(jsonfilter)
    download_log.insert(END,f'{namelist[num]}：{lenth}个文件\n')
    if os.path.isdir(f"./{manganame}/{namelist[num]}"):
        pass
    else:
        os.mkdir(f"./{manganame}/{namelist[num]}")
    dlgrid = int(re.search('Thread-(\d+)',str(threading.currentThread())).group(1))-1
    pbf = Frame(download_frame)
    pbf.grid(row=dlgrid//5+1,column=dlgrid%5+1,padx=8,pady=8)
    pbn = Label(pbf,text=f'{namelist[num]}')
    pbn.pack(side='top',anchor='center',padx=2,pady=2)
    pb = Progressbar(pbf)
    pb.pack(side='left',anchor='center',padx=2,pady=2)
    pb['maximum'] = lenth
    pb['value'] = 0
    for listname in jsonfilter:
        dlurl = listname['url']
        cache = requests.get(dlurl)
        with open(f"./{manganame}/{namelist[num]}/{filename}.jpg",'wb') as w:
            w.write(cache.content)
            w.close
        download_log.insert(END,f"成功下载图片：{namelist[num]}，{filename}.jpg，{counter}/{lenth}\n")
        download_log.see(END)
        pb['value'] =counter
        window.update()
        counter = counter + 1
        filename=str(counter).zfill(4)
    pb.pack_forget()
    pbn.pack_forget()
    pbn = Label(pbf,text=f'{namelist[num]}下载完成')
    pbn.pack(side='top',anchor='center',padx=5,pady=5)

#联网检测窗口
check_frame = Frame(window)
check_frame.pack(expand='true')

check_urllabel = Label(check_frame,text=f'当前网址：{mainurl}，该网址{validate}')

check_url = Entry(check_frame, width=25,textvariable=dispurl)
check_url.grid(row=1, column=0,padx=5,pady=5)

check_button = Button(check_frame, text="替换网址", bg="lightblue", width=8,command=check1)
check_button.grid(row=1, column=1,padx=5,pady=5)

#搜索窗口
searchdispname = StringVar()

search_frame = Frame(window)
search_frame.pack_forget()

search_label = Label(search_frame, text="在此输入要找的漫画名")
search_label.grid(row=3, column=0,padx=5,pady=5)

search_entry = Entry(search_frame, width=30,textvariable=searchdispname)
search_entry.grid(row=4, column=0,padx=5,pady=5)

search_button = Button(search_frame, text="搜索", bg="lightblue", width=5, command=search_start)
search_button.grid(row=4, column=1,padx=5,pady=5)


#搜索结果窗口
search_result_frame = Frame(window)
search_result_frame.pack_forget()

result_search_label = Label(search_result_frame, text="搜索结果")
result_search_label.grid(row=0, column=0)

result_search_list = Listbox(search_result_frame,selectmode = 'single',width=40, height=30)
result_search_list.grid(row=1,column=0,rowspan=4,padx=5,pady=5)

result_button = Button(search_result_frame, text="选择", bg="lightblue", width=5,command=searchdetail)
result_button.grid(row=2, column=1,padx=5,pady=5)

#章节选择窗口
chapter_frame = Frame(window)
chapter_frame.pack_forget()

chapter_label = Label(chapter_frame, text="章节列表")
chapter_label.grid(row=0, column=1)

chapter_bar= Scrollbar(chapter_frame)
chapter_bar.grid(row=1, column=2,sticky=NS)

chapter_list = Text(chapter_frame,yscrollcommand=chapter_bar.set,width=25)
chapter_bar.config(command=chapter_list.yview)

selector_label = Label(chapter_frame, text="下载范围")
selector_label.grid(row=2, column=1)

selector1_label = Label(chapter_frame, text="至")
selector1_label.grid(row=3, column=1)

chapter_selector = Combobox(chapter_frame)
chapter_selector.grid(row=3,column=0)

chapter_selector1 = Combobox(chapter_frame)
chapter_selector1.grid(row=3,column=3)

chapter_button = Button(chapter_frame, text="下载", bg="lightblue", width=5,command=downloadwindow)
chapter_button.grid(row=4, column=1,padx=5,pady=5)

#下载窗口
download_frame = Frame(window)
download_frame.pack_forget()

download_label = Label(download_frame,text='下载进度')
download_label.grid(row=0,column=3)


download_log = Text(download_frame,height=20)
download_log.grid_forget()

init_window()
grab(mainurl)
check()
window.mainloop()
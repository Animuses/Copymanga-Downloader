#By Animuses
from encodings import utf_8
import os
import json
import requests
from urllib import parse
import re
from Crypto.Cipher import AES
import binascii


#创建函数
#联网检测函数
def grab(mainurl):
    #当前有效网址
    print ("确认当前网站地址有效性: " + mainurl)
    confirm1=str(requests.get(f'https://{mainurl}'))
    confirm2="<Response [200]>"
    if confirm1==confirm2:
            print('当前地址有效！')
    else:
        mainurl = input('当前网站地址失效，在此输入新的地址')
        grab(mainurl)

#下载函数
def download(num):
    counter = 1
    filename = str(counter).zfill(4)
    cpurl = f'https://api.{mainurl}/api/v3/comic/{pathword}/chapter/{uuidlist[num]}'
    reqget = requests.get(cpurl)
    getjson = reqget.json()
    jsonfilter=getjson['results']['chapter']['contents']
    if os.path.isdir(f"./{manganame}/{namelist[num]}"):
        pass
    else:
        os.mkdir(f"./{manganame}/{namelist[num]}")
    for listname in jsonfilter:
        dlurl = listname['url']
        cache = requests.get(dlurl)
        with open(f"./{manganame}/{namelist[num]}/{filename}.jpg",'wb') as w:
            w.write(cache.content)
            w.close
        print(f"成功下载图片{filename}.jpg")
        counter = counter + 1
        filename=str(counter).zfill(4)


#联网检测
mainurl = 'copymanga.site'
grab(mainurl)

#漫画搜索
searchname=parse.quote(input('请输入你想要搜索的漫画名称:'))
searchurl = f'https://{mainurl}/api/kb/web/searchs/comics?offset=0&platform=2&limit=12&q={searchname}'
searchreq = requests.get(searchurl)
searchjson  = searchreq.json()
resultlist = searchjson['results']['list']
scounter = 1
pathwordlist = [0]
manganamelist = [0]
for results in resultlist:
    resultname = results['name']
    resultalias = results['alias']
    resultauthorlist = results['author']
    pathwords = results['path_word']
    for resultauthors in resultauthorlist:
        resultauthor = resultauthors['name']
        break
    print(f'\n{scounter}：\n名称：{resultname}\n又名：{resultalias}\n作者：{resultauthor}')
    pathwordlist.insert(scounter,pathwords)
    manganamelist.insert(scounter,resultname)
    scounter = scounter + 1

#选择搜索结果
selector=int(input('请输入选择的漫画序号:'))
manganame = manganamelist[selector]
pathword = parse.quote(pathwordlist[selector])
print(f'已选择：{manganame}，漫画路径为{pathword}')

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
print(cplist)


#处理章节列表并显示
listjson = json.loads(cplist)
groups = listjson['groups']
groupnum = 1
cpnum = 1
namelist = [0]
uuidlist = [0]
for grouplist in groups:
    groupname = groups[grouplist]['name']
    print(f'\n{groupnum}：{groupname}')
    groupnum = groupnum + 1

    for chapterlist in groups[grouplist]['chapters']:
        chaptername = chapterlist.get('name')
        chapteruuid = parse.quote(chapterlist['id'])
        namelist.insert(cpnum,chaptername)
        uuidlist.insert(cpnum,chapteruuid)
        print(f'--{cpnum}：{namelist[cpnum]}')
        cpnum = cpnum + 1

#选择章节
dlchoices = int(input('请输入下载范围起始序号:'))
dlchoicee = int(input('请输入下载范围终止序号:'))



#下载
if os.path.isdir(f"./{manganame}"):
    pass
else:
    os.mkdir(f"./{manganame}")
i = 0
for i in range(dlchoices,dlchoicee + 1):
    dlchoicer = dlchoicee - i
    print(f'正在下载{i}：{namelist[i]}，待下载章节数：{dlchoicer}')
    download(i)
else:
    print('下载结束')





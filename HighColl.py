from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
import sys
import time
import re
#--------------------------
streamer=''             #twitch id
cf=0                   #combineflag
pf=1                    #printflag
ascsort=1               #ascending sort 오름차순
top=10                  #영상수
transition=0            #장면전환
intro=0                 #인트로
outtro=0                #아웃트로
#--------------------------
st=3 #sleeptime
sourcehtml=[]
sourcetitle=[]

#chromedriver
url='https://www.twitch.tv/'+streamer+'/clips?filter=clips&range=7d'
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome('chromedriver' , chrome_options=options)
if pf:
    print('드라이버on')
    
#cliplink
driver.get(url)
time.sleep(st)
req = driver.page_source
resource=BeautifulSoup(req, 'html.parser')
i=0
for anchor in resource.find_all('a', class_="tw-full-width tw-interactive tw-link tw-link--hover-underline-none tw-link--inherit"):
    sourcehtml.insert(i,anchor.get('href', '/'))
    i+=1
for title in resource.find_all('h3', class_="tw-ellipsis tw-font-size-5"):
    sourcetitle.insert(i,title.get_text())
j=0
for j in range(len(sourcetitle)):
    sourcetitle[j] = re.sub('[^0-9a-zA-Zㄱ-힗]', '', sourcetitle[j])

if pf:
    print('클립주소: ')
    print(sourcehtml)
    print('클립이름: ')
    print(sourcetitle)
if i==0:
    if pf:
        print('클립이 없음')
    driver.quit()
    sys.exit(1)
if i<top:
    top=i
    if pf:
        print(str(i)+'개의 클립')

i=0
driver.quit()

#download clip
for i in range(top):
    if pf:
        print(str(i+1)+'번째 다운로드 시작')
    url='https://www.twitch.tv'+sourcehtml[i]
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome('chromedriver' , chrome_options=options)
    driver.get(url)
    time.sleep(st)

    url_element = driver.find_element_by_tag_name('video')
    vid_url = url_element.get_attribute('src')
    if cf:
        urlretrieve( vid_url,'clips/'+str(i)+'.mp4')
    else:
        urlretrieve( vid_url,'clips/'+str(i)+'.'+sourcetitle[i]+'.mp4')
    if pf:
        print(str(i+1)+'번째 완료')
    driver.quit()

#클립합치기
if cf:
    print('영상 합치는중...')
    clip=[]
    i=0
    for i in range(top):
        clip.append(VideoFileClip('clips/'+str(i)+'.mp4'))
        print(str(i+1)+'번째 합치는중')
    if ascsort:
        clip.reverse()
    if transition:
        for i in reversed(range(1,top-1)):
            clip.insert(i,VideoFileClip('clips/transition.mp4'))
    if intro:
         clip.insert(0,VideoFileClip('clips/intro.mp4'))
    if outtro:
         clip.append(VideoFileClip('clips/outtro.mp4'))
    finalclip=concatenate_videoclips(clip)
    finalclip.write_videofile('clips/highlight.mp4', threads=4, logger=None)
    print('종료')

#파이썬 설치(패쓰부분 체크) pip install bs4, pip install selenium,pip install moviepy 크롬 드라이버(https://chromedriver.chromium.org/downloads)

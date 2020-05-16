from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
import time
import re
import sys
import requests
import os
from datetime import datetime

# --------------------------

gb_combine = True  # combineflag
gi_top = 10  # 영상수
gs_intro_clip = 'clips/Intro.mp4'
gs_outro_clip = 'clips/Outro.mp4'
gf_fadein = 1.5
gf_fadeout = 1.5
gs_textclip_duration = '0:0:2'
gs_title = '주간 클립 하이라이트'  #하이라이트 영상 
gs_streamer_id = 'xxxmind'  # twitch id 입력
gs_option = '7d'  # '7d' / '30d' / 'all' 중 하나
# --------------------------
gi_sleep = 3  # sleeptime


def get_html(s_url: str) -> str:
    s_html: str = ''
    c_resp = requests.get(s_url)
    if c_resp.status_code == 200:
        s_html = c_resp.text

    return s_html


def collect_info( s_url : str ):
    htmls = []
    creators = []
    titles = []

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('--log-level=3')

    driver = webdriver.Chrome('chromedriver', chrome_options=options)
    driver.get(s_url)
    time.sleep(gi_sleep)
    c_resrc = BeautifulSoup(driver.page_source, 'html.parser')

    for item in c_resrc.find_all('a', class_='tw-full-width tw-interactive tw-link tw-link--hover-underline-none tw-link--inherit'):
        htmls.append(item.get('href', '/'))

    for item in c_resrc.find_all('a', class_='tw-interactive tw-link tw-link--hover-underline-none tw-link--inherit'):
        creators.append(item.get('href', '/')[1:])

    for item in c_resrc.find_all('h3', class_='tw-ellipsis tw-font-size-5'):
        titles.append(item.get_text())

    for j in range(len(titles)):
        titles[j] = re.sub('[^0-9a-zA-Zㄱ-힗]', '', titles[j])

    for j in range(len(htmls)):
        print('{} : {}({}) by {}'.format(j + 1, titles[j], htmls[j], creators[j]))

    driver.quit()
    return htmls, creators, titles


def download_clips(i_top, htmls, creators, titles):
    i_len = len(htmls)
    if i_len == 0:
        return 0

    if i_len < i_top:
        i_top = i_len

    for i in range(i_top):
        s_url = 'https://www.twitch.tv' + htmls[i]
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--log-level=3')
        driver = webdriver.Chrome('chromedriver', chrome_options=options)
        driver.get(s_url)

        time.sleep(gi_sleep)

        url_element = driver.find_element_by_tag_name('video')
        vid_url = url_element.get_attribute('src')
        s_path = 'clips/{}_{}.mp4'.format(i, titles[i])
        urlretrieve(vid_url, s_path)
        print('downloading {} completed.'.format(i + 1))
        driver.quit()

    return i_top


def combine_videos(i_clips : int, titles):
    clips = []
    c_titleclip = TextClip(txt=gs_title, color='white', fontsize=60, font='Malgun-Gothic').set_duration(gs_textclip_duration)
    for i in range(i_clips):
        s_path = 'clips/{}_{}.mp4'.format(i, titles[i])
        begin = time.time()

        s_text = 'No {}. {}'.format(i + 1, titles[i])
        c_overlay_clip = TextClip(txt=s_text, color='white', fontsize=30, font='Malgun-Gothic')
        c_textclip = c_overlay_clip.set_duration(gs_textclip_duration)
        c_clip = VideoFileClip(s_path)
        c_composite_clip = CompositeVideoClip([c_clip, c_overlay_clip.set_position(('left', 'top'))])
        c_composite_clip = c_composite_clip.set_duration(c_clip.duration)
        c_composite_clip = c_composite_clip.fadein(gf_fadein)
        c_composite_clip = c_composite_clip.fadeout(gf_fadeout)
        clips.append(c_composite_clip)
        clips.append(c_textclip)
        end = time.time()

        print('completing {} took {:.2} sec'.format(s_path, end - begin))

    clips.append(c_titleclip)
    clips.reverse()

    try:
        c_intro = VideoFileClip(gs_intro_clip)
        clips.insert(0, c_intro)
    except Exception as e:
        pass

    try:
        c_outro = VideoFileClip(gs_outro_clip)
        clips.append(c_outro)
    except Exception as e:
        pass


    s_date_time = datetime.now().strftime("%Y.%m.%d")
    s_result_path = '{}\\clips\\{}_{}.mp4'.format(os.getcwd(), s_date_time, 'highlight')

    print('wrapping up the clips...')

    begin = time.time()
    c_result_clip = concatenate_videoclips(clips, method="compose")
    c_result_clip.write_videofile(s_result_path, threads=4, logger=None)
    end = time.time()

    print('completed, took {:.2} sec'.format(end - begin))

    return


def main():
    s_url = 'https://www.twitch.tv/{}/clips?filter=clips&range={}'.format(gs_streamer_id, gs_option)
    try:
        s_path = os.getcwd()
        os.makedirs('{}/clips'.format(s_path))
    except FileExistsError:
        pass
    except Exception as e:
        print('{}'.fomat(e))

    htmls, creators, titles = collect_info(s_url)
    i_clips = download_clips(gi_top, htmls, creators, titles)
    if gb_combine:
        combine_videos(i_clips, titles)

    return


if __name__ == "__main__":
    main()


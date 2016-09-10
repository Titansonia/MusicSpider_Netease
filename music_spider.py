# coding=utf-8
import os
import time
import re
import types
from bs4 import BeautifulSoup
from selenium import webdriver
import tool

class MusicSpider:

    def __init__(self):
        self.tool = tool.Tool()

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

    def getCurrentDate(self):
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def getAllAlbumPageUrl(self,artist_id):
        return 'http://music.163.com/#/artist/album?id='+artist_id

    def getAllAlbumPageUrlByNum(self,artist_id,page_num_url):
        if page_num_url:
            page_num_url_new = str(page_num_url).replace("&amp;","&")
            return 'http://music.163.com/#/artist/album?id='+artist_id+page_num_url_new
        else:
            return 'http://music.163.com/#/artist/album?id='+artist_id

    def getMusicPageUrl(self,album_id):
        return 'http://music.163.com/#/album?id='+album_id

    def getLyricsPageUrl(self,music_id):
        return 'http://music.163.com/#/song?id='+music_id

    #返回当前页面的html文本
    def getPageByUrl(self,url):
        driver = webdriver.PhantomJS()
        driver.get(url)
        driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
        content = driver.page_source
        return content

    #获得歌手所有专辑页面每一个页码的url和总页码数,返回url列表
    def getTotalPageNumUrl(self,artist_id):
        print self.getCurrentDate(),self.getCurrentTime(),'Info:正在获取歌曲所有专辑页面的全部url和总页码数'
        page_num_url_list = []
        total_page_num = 1
        url = self.getAllAlbumPageUrl(artist_id)
        content = self.getPageByUrl(url)
        soup = BeautifulSoup(content,"html.parser")
        result  = soup.select('a[class="zpgi"]')
        if len(result)>0:
            for page_num_url in result:
                if not type(page_num_url) is types.StringType:
                    page_num_url = str(page_num_url)
                page_num_url_match = re.search(re.compile(u'<a class="zpgi" href="/artist/album\?id='+artist_id+'(.*?)">(.*?)</a>',re.S),page_num_url)
                if page_num_url_match:
                    page_num_url = page_num_url_match.group(1)
                    total_page_num = page_num_url_match.group(2)
                    page_num_url = self.getAllAlbumPageUrlByNum(artist_id,page_num_url)
                    page_num_url_list.append(page_num_url)
                else:
                    return None
            print self.getCurrentDate(),self.getCurrentTime(),'Info:歌手所有专辑页面总页码数为 '+total_page_num
        else:
            print self.getCurrentDate(),self.getCurrentTime(),'Info:歌手所有专辑页面总页码数为 1'
        return page_num_url_list


    # http://music.163.com/#/artist/album?id='+artist_id
    # 返回某一歌手的所有专辑信息,包括专辑id,name,date,要考虑分页问题
    def getAlbumInfo(self,artist_id):
        print self.getCurrentDate(),self.getCurrentTime(),'Info:正在获取歌手'+artist_id+'的专辑信息'
        album_info_list = []
        page_num_url_list = []
        url = self.getAllAlbumPageUrl(artist_id)
        page_num_url_list = self.getTotalPageNumUrl(artist_id)
        page_num_url_list.insert(0,url)

        for page_num_url in page_num_url_list:
            content = self.getPageByUrl(page_num_url)
            soup = BeautifulSoup(content,"html.parser")
            result = soup.select('#m-song-module li')
            if result:
                for album in result:
                    if not type(album) is types.StringType:
                        album = str(album)
                    album_id_match = re.search(re.compile(u'.*?<a class="msk".*?/album\?id=(.*?)">',re.S),album)
                    album_name_match = re.search(re.compile(u'.*?<p class="dec" title="(.*?)">',re.S),album)
                    album_date_match = re.search(re.compile(u'.*?<span class="s-fc3">(.*?)</span>',re.S),album)
                    if album_id_match and album_name_match:
                        album_id = album_id_match.group(1)
                        album_name = album_name_match.group(1)
                        album_name = album_name.replace("&amp;","&")
                        if album_date_match:
                            album_date = album_date_match.group(1)
                        else:
                            album_date = ''
                        album_info = [album_id,album_name,album_date]
                        album_info_list.append(album_info)
                    else:
                        print self.getCurrentDate(),self.getCurrentTime(),'Error:无法获取专辑id或name'
            else:
                print self.getCurrentDate(),self.getCurrentTime(),'Error:无法查询到歌手专辑'
        return album_info_list

    def makeAlbumDir(self,artist_name,album_name,album_date):
        print self.getCurrentDate(),self.getCurrentTime(),'Info:创建专辑'+album_name+'的目录'
        try:
            os.mkdir('/Users/titansonia/Documents/lyrics/'+artist_name+'/'+album_name+album_date)
        except Exception,e:
            print self.getCurrentDate(),self.getCurrentTime(),e


    #http://music.163.com/#/album?id='+album_id
    #获取某一张专辑中的所有歌曲信息,包括歌曲id和name
    def getMusicInfo(self,album_id):
        print self.getCurrentDate(),self.getCurrentTime(),' Info:正在获取专辑'+album_id+'中的歌曲信息'
        music_info_list = []
        url = self.getMusicPageUrl(album_id)
        content = self.getPageByUrl(url)
        soup = BeautifulSoup(content,"html.parser")
        result = soup.findAll("span",class_="txt")
        for music in result:
            if not type(music) is types.StringType:
                music = str(music)
            music_id_match = re.search(re.compile(u'.*?<a href="/song\?id=(.*?)">',re.S),music)
            music_name_match = re.search(re.compile(u'.*?<b title="(.*?)">',re.S),music)
            if music_id_match and music_name_match:
                music_id = music_id_match.group(1)
                music_name = music_name_match.group(1)
                music_info = (music_id,music_name)
                music_info_list.append(music_info)
            else:
                print self.getCurrentDate(),self.getCurrentTime(),'Error:无法获得歌曲id或name'
        return music_info_list

    def makeLyricFile(self,artist_name,album_name,album_date,music_name):
        print self.getCurrentDate(),self.getCurrentTime(),'Info:创建歌曲'+music_name+'的目录'
        try:
            f=open("/Users/titansonia/Documents/lyrics/"+ artist_name +"/" + album_name + album_date + "/" + music_name + ".txt",'w')
            f.close()
        except Exception,e:
            print self.getCurrentDate(),self.getCurrentTime(),e

    #http://music.163.com/#/song?id='+music_id
    #获得某一首歌的歌词信息,仅包括歌词
    def getLyrics(self,music_id):
        lyrics = ''
        url = self.getLyricsPageUrl(music_id)
        content = self.getPageByUrl(url)
        soup = BeautifulSoup(content,"html.parser")
        result = soup.select('#lyric-content')
        if len(result)>0:
            if not type(result[0]) is types.StringType:
                result = str(result[0])
            lyric_match = re.search(re.compile(u'.*?<div.*?id="lyric-content".*?>(.*?)</div>',re.S),result)
            if lyric_match:
                lyrics = lyric_match.group(1)
                lyrics = self.tool.replace(lyrics)
        else:
            print self.getCurrentDate(),self.getCurrentTime(),"Alert:当前歌曲无歌词"
        return lyrics


    def writeLyrics(self,artist_name,album_name,album_date,music_name,lyrics):
        print self.getCurrentDate(),self.getCurrentTime(),'Info:写入歌曲'+music_name+'的歌词'
        try:
            f=open("/Users/titansonia/Documents/lyrics/"+ artist_name + "/" + album_name + album_date + "/" + music_name + ".txt",'w')
            f.write(lyrics)
            f.close()
        except Exception,e:
            print self.getCurrentDate(),self.getCurrentTime(),e

    #判断专辑目录是否
    def album_exists(self,artist_name,album_name,album_date):
        return os.path.exists('/Users/titansonia/Documents/lyrics/'+artist_name+'/'+album_name+album_date)

    #判断歌词是否存在
    def lyrics_exists(self,artist_name,album_name,album_date,music_name):
        if_exists = os.path.exists("/Users/titansonia/Documents/lyrics/"+ artist_name + "/" + album_name + album_date + "/" + music_name + ".txt")
        if if_exists:
            if os.path.getsize("/Users/titansonia/Documents/lyrics/"+ artist_name + "/" + album_name + album_date + "/" + music_name + ".txt"):
                return True
            else:
                return False
        else:
            return False



    def main(self,artist_id,artist_name):
        albums = self.getAlbumInfo(artist_id)
        for album in albums:
            album_id = album[0]
            album_name = album[1]
            album_date = album[2]
            if not self.album_exists(artist_name,album_name,album_date):
                self.makeAlbumDir(artist_name,album_name,album_date)
            musics = self.getMusicInfo(album_id)
            for music in musics:
                music_id = music[0]
                music_name = music[1]
                #self.makeLyricFile(artist_name,album_name,album_date,music_name)
                lyrics = self.getLyrics(music_id)
                if str(lyrics) not in ['','暂时没有歌词求歌词','纯音乐，无歌词']:
                    if not self.lyrics_exists(artist_name,album_name,album_date,music_name):
                        self.writeLyrics(artist_name,album_name,album_date,music_name,lyrics)

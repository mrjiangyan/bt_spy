import requests
from bs4 import BeautifulSoup
from data.service.bt_torrent_service import get_by_unicode, get_max_unicode_by_type
from data.model.t_bt_torrent import BtTorrent
from data.enum.model_type_enum import SourceTypeEnum
from data import database
import re
from loguru import logger

def check_image_exists(image_url):
    try:
        response = requests.head(image_url)
        return response.status_code == 200
    except requests.RequestException:
        return False
    
def get_page_info(url):
    try:
        # 发送 GET 请求获取网页内容
        response = requests.get(url)

        # 检查 HTTP 响应状态码
        if response.status_code == 200:
            print(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取页面标题
            page_title = soup.title.string.strip()

            # 获取页面中的所有链接
            links = soup.find_all('a', href=True)

            # 获取包含特定关键字的 img 节点的 file 属性
            cover = soup.find_all('img', class_='zoom')
            cover = [img['file'] for img in cover if check_image_exists(img['file'])]

            magnet_links = [link['href'] for link in links if link['href'].startswith('magnet:')]
            
            images = [img['file'] for img in soup.find_all('img', attrs={'file': re.compile(r'img2\.doubanio\.com')})]

            
            # 构建包含标题、页面链接和页面内链接的字典
            page_info = {
                "title": page_title.replace(' - 4K电影美剧下载 - HDR杜比视界资源 -  4KHDR世界 -  4KHDR.CN',''),
                "page_url": url,
                "torrent": ','.join(magnet_links),
                "cover": cover[0] if cover and len(cover) > 0 else '',  # 如果cover不为None且长度大于0，则取cover的第一个元素，否则为''
                "images": ','.join(images)
            }
            parseHtml(soup, page_info)
            return page_info
        else:
            print(f"Page does not exist. Status Code: {response.status_code}")
    except requests.RequestException as e:
        print("Error:", e)
        return None


def find_douban_link(soup, patterns, logger, page_info):
    for pattern in patterns:
        douban_links = soup.find_all('a', href=pattern)
        if douban_links:
            page_info["douban_link"] = douban_links[0].get_text(strip=True)
            logger.info(f"douban_link:{page_info['douban_link']}")
            return
        else:
            douban_links = soup.find_all('a', string=pattern)
            if douban_links:
                page_info["douban_link"] = douban_links[0].get_text(strip=True)
                logger.info(f"douban_link:{page_info['douban_link']}")
                return
def find_imdb_link(soup, patterns, logger, page_info):
    for pattern in patterns:
        douban_links = soup.find_all('a', href=pattern)
        if douban_links:
            page_info["imdb_link"] = douban_links[0].get_text(strip=True)
            logger.info(f"imdb_link:{page_info['imdb_link']}")
            return
        else:
            douban_links = soup.find_all('a', string=pattern)
            if douban_links:
                page_info["imdb_link"] = douban_links[0].get_text(strip=True)
                logger.info(f"imdb_link:{page_info['imdb_link']}")
                return


def parseHtml(soup: BeautifulSoup, page_info):
    
    # 定义模式列表
    patterns = [
        re.compile(r'https://movie\.douban\.com/subject/\S+/'),
        re.compile(r'https://douban\.com/subject/\S+/'),
        re.compile(r'http://movie\.douban\.com/subject/\S+/'),
        re.compile(r'http://douban\.com/subject/\S+/'),
    ]
    # 调用函数查找豆瓣链接
    find_douban_link(soup, patterns, logger, page_info)
    
    patterns = [
        re.compile(r'https://www\.imdb\.com/title/\S+'),
        re.compile(r'https://www\.imdb\.com/title/\S+/'),
        re.compile(r'http://www\.imdb\.com/title/\S+'),
        re.compile(r'http://www\.imdb\.com/title/\S+/'),
    ]
        
    find_imdb_link(soup, patterns, logger, page_info)
    
    keyword = '◎译　　名'
    first_element_with_keyword = soup.find(lambda tag: keyword.lower() in tag.text.lower())

    # If the element is found, extract the surrounding text
    if first_element_with_keyword:
        surrounding_text = first_element_with_keyword.get_text(strip=True)
        # print("Surrounding text:", surrounding_text)
       
        result = re.search(r'◎年　　代　(\d+)', surrounding_text)
        if result:
            
            year = result.group(1)
            page_info["year"] = year
            logger.info(f"year:{year}")
            
        result = re.search(r'◎产　　地　([^◎]+)◎', surrounding_text)
        if result:
            country = result.group(1)
            page_info["country"] = country
            logger.info(f"country:{country}")
           
        result = re.search(r'◎类　　别　([^◎]+)◎', surrounding_text)
        if result:
            category = result.group(1)
            page_info["category"] = category
            logger.info(f"category:{category}")
            
        result = re.search(r'◎上映日期　([^◎]+)◎', surrounding_text)
        if result:
            release_date = result.group(1)
            page_info["release_date"] = release_date
            logger.info(f"release_date:{release_date}")
          
        result = re.search(r'◎语　　言　([^◎]+)◎', surrounding_text)
        if result:
            language = result.group(1)
            page_info["language"] = language
            logger.info(f"language:{language}")
        
     

# 需要设置增量模式还是更新模式

def spy(incremental_mode=True):
    logger.info('spy_4khdr_cn')
    index = 0
    with database.create_session() as db_sess:    
        if incremental_mode:  
            torrent = get_max_unicode_by_type(db_sess, SourceTypeEnum._4khdr_cn)
            if torrent:
                index = torrent.unicode
        for i in range(int(index)+1, 6900):
                website_url = f"https://www.4khdr.cn/thread-{i}-1-1.html"
                page_info = get_page_info(website_url)
                if page_info:
                    if incremental_mode == False:
                        torrent = get_by_unicode(db_sess, SourceTypeEnum._4khdr_cn, i)  
                    if torrent is None:
                        torrent = BtTorrent()
                        torrent.unicode = i
                        torrent.type = SourceTypeEnum._4khdr_cn.value  
                        torrent.url = page_info.get("page_url")
                    
                    
                    attributes_to_update = ["title","year", "country", "language", "category", "release_date", "imdb_link", "douban_link", "cover", "images", "torrent"]
                    for attribute in attributes_to_update:
                        if attribute in page_info:
                            setattr(torrent, attribute, page_info[attribute])
                    # 新增1条记录
                    if torrent.id != None:
                        # 如果记录已经存在于数据库中，使用 merge 进行更新
                        db_sess.merge(torrent)
                    else:
                        db_sess.add(torrent)
                    db_sess.commit()

            
     
 
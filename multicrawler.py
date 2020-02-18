from bs4 import BeautifulSoup
from collections import deque
import urllib.parse
import queue
import json
import urllib.error
import urllib.request
import urllib.robotparser
import threading
import os
import re
import logging
import requests
import mainc as m


BASE_PROTOCOL = m.BASE_PROTOCOL
START_URL = ''
THREADS_COUNT = 1
ISUPDATE = ''
REGIME = False
folder = ''


class Crawler:
    def __init__(self, urls):
        self.checked = deque()
        self.q = deque()
        self.temp = deque()
        for url in urls:
            self.q.append(url)

    def crawl(self):
        for page in list(self.q):
            try:
                urls = cut_urls(page)
                for item in urls:
                    self.temp.append(item)
            except UnicodeError:
                try:
                    urls = cut_urls(page, encoding='cp1251')
                    for item in urls:
                        self.temp.append(item)
                except UnicodeError:
                    continue
            except urllib.error.URLError:
                print('URL Error has occurred')
                continue
        self.checked = self.q.copy()
        self.q = self.temp.copy()
        self.temp.clear()


def may_fetch(robots_page, page_to_crawl):
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_page)
    parser.read()
    return parser.can_fetch('*', page_to_crawl)


def download(queue, folder_name, file_name="", debug=False):
    logging.basicConfig(filename='crawler.log', level=logging.INFO)
    items_queue = []
    while not queue.empty():
        item = queue.get()
        get_text_content(item, os.path.join(folder, f"{item.split('/')[-1]}.txt"))
        download_pics(cut_images(item), os.path.join(folder, "pics"))
        try:
            items_queue.append(item)
            d = {"links": {"current": item, "queue": items_queue}}
            write_current_link_in_json("crawler_links.json", d)
            os.makedirs(folder_name, exist_ok=True)
            if not file_name:
                filename = f"{folder_name}/{''.join(item.split('/')[-2:])}.html"
            else:
                filename = f"{folder_name}/{file_name}.html"
            if os.path.exists(filename):
                print(f"{item} is already downloaded")
                continue
            if not debug:
                response = urllib.request.urlopen(item)
            else:
                while item in get_current_link_and_links("crawler_links.json")[1]:
                    item = queue.get()
                response = urllib.request.urlopen(item)
            with open(filename, "wb") as f_handler:
                while True:
                    chunk = response.read(1024)
                    if not chunk:
                        break
                    f_handler.write(chunk)
            #rewrite_html(filename)
            msg = f'{item} is downloaded'
            print(msg)
        except urllib.error.HTTPError:
            logging.info(f'source {item} was not downloaded because it was not found')
        except urllib.error.URLError:
            logging.info(f'source {item} was not downloaded because it was not found')
        except UnicodeError:
            logging.info(f"source {item} wasn't downloaded because of a Unicode error")
        except TypeError:
            logging.info(f"source {item} wasn't downloaded because of a Unicode error")


def cut_urls(page, encoding='utf-8'):
    content = urllib.request.urlopen(page).read().decode(encoding=encoding)
    soup = BeautifulSoup(content, 'html.parser')
    normed = [canonization_url(link.get('href')) for link in soup.find_all('a')]
    return list(filter(None, normed))


def canonization_url(url):
    if url is not None:
        if BASE_PROTOCOL not in url:
            url = START_URL + url
        parts_url = urllib.parse.urlsplit(url.strip())
        res = urllib.parse.urlunsplit(
            (parts_url.scheme, parts_url.netloc, parts_url.path,
                parts_url.query, ''))
        return re.sub(r'(?::\d+)*', '', res.lower().strip('/.'))
    return ''


def normalize_references(references, protocol, domain):
    images = []
    for ref in references:
        if not ref.startswith(domain) and not ref.startswith(protocol):
            ref = "/".join([domain, ref.strip("/")])
        if not ref.startswith(protocol):
            ref = "//".join([protocol, ref.strip("/")])
        images.append(ref)
    return images


def cut_images(url):
    try:
        page = requests.get(url)
        splited = url.split("/")[:3]
        protocol = splited[0]
        domain = splited[2]
        image_refs = re.findall(r"<img .*src=\".*?\"", page.content.decode(encoding="utf8"))
        image_refs = [re.match(r"<img .*src=\"(.*)\"", ref).group(1) for ref in image_refs]
        return normalize_references(image_refs, protocol, domain)
    except requests.exceptions.ConnectionError:
        print("URL is unreachable")


def multithreading_downloading(urls, urls_to_download,
                               file_name, folder_to_store_downloaded):
    urllib.request.urlopen(file_name)
    for i in range(len(urls)):
        if may_fetch(START_URL + 'robots.txt', urls[i]):
            urls_to_download.put(urls[i])
    threads = []
    for j in range(THREADS_COUNT):
        t = threading.Thread(target=download,
                             args=(urls_to_download,
                                   folder_to_store_downloaded),
                             kwargs={"debug": REGIME})
        threads.append(t)
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()


def main(crawl_obj, folder_to_save):
    urls = crawl_obj.q
    urls_to_download = queue.Queue()
    try:
        multithreading_downloading(
            urls, urls_to_download, START_URL + 'robots.txt',
            folder_to_save, )
    except urllib.error.URLError:
        print('Page %s does not support \'robots.txt\'' % START_URL)
        multithreading_downloading(urls, urls_to_download,
                                   START_URL, folder_to_save)


def write_current_link_in_json(json_file, link):
    with open(json_file, 'w') as jf:
        json.dump(link, jf)


def get_current_link_and_links(json_file):
    with open(json_file, 'r') as jf:
        json_string = jf.readline()
        data = json.loads(json_string)["links"]
        return data["current"], data["queue"]


def get_text_content(url, file_name):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    with open(file_name, 'w', encoding="utf8", errors="ignore") as f:
        f.write(text)


def download_pics(pics, path):
    for pic in pics:
        try:
            name = re.sub(r"[=?%\-+]", '', pic.split("/")[-1])
            name = norm_file_name(name)
            urllib.request.urlretrieve(pic, os.path.join(path, name))
        except UnicodeError:
            continue
        except urllib.error.HTTPError:
            continue


def norm_file_name(supposed_name):
    if supposed_name.endswith((".jpg", ".jpeg", ".svg", ".png")):
        return supposed_name
    return f"{supposed_name}.jpg"


def get_hashcode(page):
    with open(os.path.join(os.getcwd(), ISUPDATE, page), "rb") as f_handler:
        return hash(f_handler.read())


def rewrite_html(page):
    with open(page, 'r+') as page_file:
        data = page_file.read()
    image_refs = re.findall(r"<img .*src=\".*?\"", data)
    image_refs = [re.match(r"<img .*src=\"(.*)\"", ref).group(1) for ref in image_refs]
    img_names = [ref.replace('-', '') for ref in image_refs]
    for img in image_refs:
        for name in img_names:
            if name in img:
                data.replace(img, os.path.join(os.getcwd(), folder, "pics", name))
    page_file.write(data)


def update_pages(folder_with_files):
    if not folder_with_files:
        pass
    path = os.path.join(os.getcwd(), folder_with_files)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    links = get_current_link_and_links("crawler_links.json")[1]
    for link in links:
        for file in files:
            name = link.split('/')[-1]
            if hash(link) == hash(file):
                if not get_hashcode(file) == get_hashcode(link):
                    response = urllib.request.urlopen(link)
                    with open(os.path.join(os.getcwd(), folder_with_files, f"{name}.html"), "wb") as f_handler:
                        while True:
                            chunk = response.read(1024)
                            if not chunk:
                                break
                            f_handler.write(chunk)
                    get_text_content(link, os.path.join(folder, f"{link.split('/')[-1]}.txt"))
                    download_pics(cut_images(link), os.path.join(folder, "pics"))

if __name__ == '__main__':
    rl = "http://www.photogallery.va/content/photogallery/en/papi/franciscus.html"
    print(cut_images(rl))

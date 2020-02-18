import argparse
import os.path
import multicrawler as script

BASE_PROTOCOL = 'http'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler. Enter a list of pages to crawl.',
                                     usage='%s -p url1 -p url2' % os.path.basename(__file__))
    parser.add_argument('-p', '--pages', type=str, action='append',
                        help='Urls to crawl')
    parser.add_argument('-t', '--threads', type=int, action='store',
                        help='Amount of threads to crawl page')
    parser.add_argument('-f', '--folder', action='store', type=str,
                        help="Folder to save downloaded data")
    parser.add_argument('--upd', type=str, help='updates downloaded stuff', default='')
    parser.add_argument('--debug', type=bool, help='call if an error occurred', default=False)
    args = parser.parse_args().__dict__
    if args['upd']:
        script.update_pages(args['upd'])
    else:
        URLS = args['pages']
        script.REGIME = args['debug']
        script.ISUPDATE = args['upd']
        FOLDER_TO_DOWNLOAD = args['folder']
        os.makedirs(os.path.join(os.getcwd(), FOLDER_TO_DOWNLOAD), exist_ok=True)
        script.THREADS_COUNT = args['threads']
        script.START_URL = '/'.join(URLS[0].split('/')[:3]) + '/'
        script.folder = FOLDER_TO_DOWNLOAD

        folder = os.path.join(os.getcwd(), FOLDER_TO_DOWNLOAD)
        os.makedirs(os.path.join(folder, "pics"), exist_ok=True)

        for u in URLS:
            script.get_text_content(u, os.path.join(folder, f"{u.split('/')[-1]}.txt"))
            script.download_pics(script.cut_images(u), os.path.join(folder, "pics"))

        c = script.Crawler(URLS)
        c.crawl()
        script.main(c, FOLDER_TO_DOWNLOAD)

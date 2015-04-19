import Queue
from constant import DETAIL_URL, IMAGE_URL


class Dojinshi(object):
    def __init__(self, name=None, subtitle=None, id=None, pages=0):
        self.name = name
        self.subtitle = subtitle
        self.id = id
        self.pages = pages
        self.downloader = None
        self.url = '%s/%d' % (DETAIL_URL, self.id)

    def __repr__(self):
        return '<Dojinshi: %s>' % self.name

    def show(self):
        print 'Dojinshi: %s' % self.name
        print 'Subtitle: %s' % self.subtitle
        print 'URL: %s' % self.url
        print 'Pages: %d' % self.pages

    def download(self):
        if self.downloader:
            download_queue = Queue.Queue()
            for i in xrange(1, self.pages + 1):
                download_queue.put('%s/%d/%d.jpg' % (IMAGE_URL, self.id, i))
            self.downloader.download(download_queue)
        else:
            raise Exception('Downloader has not be loaded')


if __name__ == '__main__':
    test = Dojinshi(name='test hentai dojinshi', id=1)
    print test
    test.show()
    try:
        test.download()
    except Exception, e:
        print 'Exception: %s' % str(e)
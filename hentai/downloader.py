import threading
import Queue


class Downloader(object):
    def __init__(self):
        self.threads = []

    def _download(self, queue):
        while True:
            if not queue.qsize():
                queue.task_done()
                break
            try:
                url = queue.get(False)
                print 'Downloading: %s' % url
            except Queue.Empty:
                break

    def download(self, queue):
        for i in range(10):
            _ = threading.Thread(target=self._download, args=(queue, ))
            self.threads.append(_)

        for i in self.threads:
            i.start()

        for i in self.threads:
            i.join()


if __name__ == '__main__':
    d = Downloader()
    q = Queue.Queue()
    for i in range(0, 50):
        q.put(i)
    d.download(q)

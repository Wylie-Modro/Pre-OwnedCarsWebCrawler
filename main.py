# by William Wylie-Modro
import datetime
start = datetime.datetime.now()

import sys
import threading

is_py2 = sys.version[0] == '2'
#imports queue appropriately based on the version of python
if is_py2:
    from Queue import Queue 
    print('Running Python2')
else:
    from queue import Queue 
    print('Running Python3')

from MainCrawlerClassFile import MainCrawlerClass
from InputOutputClassFile import InputOutputClass


#Next job in multi-threaded queue
def CrawlWork():
    while True: 
        url = secondThreadQueue.get()
        #Calls function that we want run multiple times across multiple threads
        mCrawlerCls.CrawlOnePage(threading.current_thread().name, url) 
        secondThreadQueue.task_done()
        #Adds and removes url from various sets before updating queue.txt & crawled.txt
        mCrawlerCls.crawledSet.add(url)
        mCrawlerCls.queueSet.remove(url)


#Essentially takes urls from queue.txt into a set and then into the thread queue
def CreateJobs():
    for pgLink in IOCls.FileToSet(mCrawlerCls.QUEUE_FILE):
        secondThreadQueue.put(pgLink)


#Create threads (will die when main exits)
def CreateThreads():
    for _ in range(mCrawlerCls.number_of_threads_for_crawling):
        threadV = threading.Thread(target = CrawlWork)
        threadV.daemon = True
        threadV.start()

#Check if there are page links in queue.txt, if so call CreateJobs()
def BaseCrawl():
    print('BaseCrawl() called')
    queuedPagesSet = IOCls.FileToSet(mCrawlerCls.QUEUE_FILE)
    if len(queuedPagesSet) > 0:
        print(str(len(queuedPagesSet)) + ' page links in queue')
        CreateJobs()
   
   

#Input sites to be crawled
listOfSites = ['http://www.abwautos.com/vehicles?Page=1','http://www.appleautoct.com/inventory?pagin=1&ipp=All&','http://www.irwinhyundai.com/searchused.aspx?pt=3']

#Instantiate Classes
mCrawlerCls = MainCrawlerClass(listOfSites, 'QueuednCrawledFiles')#Among other things this will put the above links in queue.txt
IOCls = InputOutputClass()
secondThreadQueue = Queue()

BaseCrawl() #Check if there are links in queue.txt, if so will put them in the thread queue
CreateThreads()

secondThreadQueue.join() #Let all the thread catch up to each other

#Essentially takes in the domain names, and outputs the respective txt files
mCrawlerCls.SortMasterDictToOutputFiles('www.abwautos.com', 'www.appleautoct.com', 'www.irwinhyundai.com')


#-----Can Read Files Back In Using Common Read-In Methods-----
#IOCls.ReadTabDelFileManually('www.abwautos.com.txt')
#IOCls.ReadTabDelFileCSV('www.abwautos.com.txtt')

#IOCls.ReadTabDelFileManually('www.appleautoct.com.txt')
#IOCls.ReadTabDelFileCSV('www.appleautoct.com.txt')

#IOCls.ReadTabDelFileManually('www.irwinhyundai.com.txt')
#IOCls.ReadTabDelFileCSV('www.irwinhyundai.com.txt')

    
#To get approximate speed of Program
finish = datetime.datetime.now()
print("\nTime:" + str(finish-start) + 's')



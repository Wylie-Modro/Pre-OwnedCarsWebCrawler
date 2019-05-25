import threading
import sys

is_py2 = sys.version[0] == '2'
#imports queue appropriately based on the version of python
if is_py2:
    from Queue import Queue 
else:
    from queue import Queue 

#from queue import Queue 

import collections as coll
import re
import requests as req
from bs4 import BeautifulSoup

from GetSingleVehicleInfoClassFile import GetSingleVehicleInfoClass
from InputOutputClassFile import InputOutputClass

class MainCrawlerClass:
    
    #Class variables
    project_name = ''
    QUEUE_FILE = ''
    CRAWLED_FILE = ''
    queueSet = set()
    crawledSet = set()
    masterDictionary = {}
    setOfAllDiscovedPages = set()
    firstThreadQueue = Queue()
    numberOfThreadsAtBootUp = 3
    
    def __init__(self, listOfWebsites, project_name):
        MainCrawlerClass.PROJECT_NAME = project_name
        MainCrawlerClass.LiST_OF_WEBSITES = listOfWebsites
        MainCrawlerClass.number_of_threads_for_crawling = 8
        MainCrawlerClass.QUEUE_FILE = project_name + '/queue.txt'
        MainCrawlerClass.CRAWLED_FILE = project_name + '/crawled.txt'
        self.BootUp(listOfWebsites)
        
        
    def BootUp(self, listOfWebsites):
        print('-----------------------------------------------------------')
        print('Start Of BootUp!')
        IOCls = InputOutputClass()
        IOCls.CreateProjectDir(MainCrawlerClass.PROJECT_NAME)
        IOCls.CreateLinkFiles(MainCrawlerClass.PROJECT_NAME) #Creates or rewrites queue.txt & crawled.txt
        MainCrawlerClass.queueSet = IOCls.FileToSet(MainCrawlerClass.QUEUE_FILE)
        MainCrawlerClass.crawledSet = IOCls.FileToSet(MainCrawlerClass.CRAWLED_FILE)
        
        MainCrawlerClass.AddLinksToQueue(listOfWebsites) #Adds inputed links to the queueSet
  
        #We will now run through every page of the sites on multiple threads to obtain all the different page links
        if len(MainCrawlerClass.queueSet) > 0:
            print(str(len(MainCrawlerClass.queueSet)) + ' sites link in queuedSet')
            for pgLink in MainCrawlerClass.queueSet:
                MainCrawlerClass.firstThreadQueue.put(pgLink) #Loads all of queueSet into threading queue
        
        #Create threads
        for _ in range(MainCrawlerClass.numberOfThreadsAtBootUp):
            threadV = threading.Thread(target = self.BootUpWork)
            threadV.daemon = True
            threadV.start()
        
        MainCrawlerClass.firstThreadQueue.join() #Let all the threads for BootUp() catch up and stop
        IOCls.ClearFileContents(MainCrawlerClass.QUEUE_FILE)
        
        #Set keys of masterDictionary
        MainCrawlerClass.masterDictionary = MainCrawlerClass.CreateDictKeys(MainCrawlerClass.setOfAllDiscovedPages)
        
        MainCrawlerClass.AddLinksToQueue(MainCrawlerClass.setOfAllDiscovedPages) #Add all the discovered pages to queueSet 
        MainCrawlerClass.UpdateQueueCrawledFiles()
        
        print('End of Bootup!')
        print('-----------------------------------------------------------')
    
    #Next job in multi-threaded queue
    def BootUpWork(self): 
        while True: 
            inventoryUrlWPgNum = MainCrawlerClass.firstThreadQueue.get()#Gets url from thread queue
            #Calls function that we want run multiple times across multiple threads
            self.GetInventorypgLink(inventoryUrlWPgNum, threading.current_thread().name) 
            MainCrawlerClass.firstThreadQueue.task_done()
       
        
    def GetInventorypgLink(self, inventoryUrlWPgNum, threadName):
        print('GetInventorypgLink() called by : ' + str(threadName))
        #Removes last digit if needed so that it can iterate through the pages
        inventoryUrlWOPgNum = self.GetUrlWOPgNum(inventoryUrlWPgNum)
        #if all inventory on one page return without modification to the url
        if (re.search(r'All', inventoryUrlWOPgNum)):
            print('One Page Inventory')
            MainCrawlerClass.setOfAllDiscovedPages.add(inventoryUrlWOPgNum)
        else:
            #if inventory over multiple pages it will iterate through them
            for pageNum in range(1, 20):
                inventoryUrlWNewNum = inventoryUrlWOPgNum + str(pageNum)
                print('Collecting Page number: ' + str(pageNum) + ' From ' + inventoryUrlWNewNum + ' by: ' + str(threadName))
                html_text = MainCrawlerClass.GetHTMLText(inventoryUrlWNewNum)
                self.CheckIfPageBlocked(inventoryUrlWNewNum,html_text) 
                soup = BeautifulSoup(html_text, "lxml") 
                MainCrawlerClass.setOfAllDiscovedPages.add(inventoryUrlWNewNum)#Adds discovered pages links to setOfAllDiscovedPages
                #If the current page is the last then break the loop 
                if (self.CheckIfLastPage(soup, html_text)):
                    break  
  
        
    @staticmethod
    def GetSiteNPageName(pgLink):
        searchForSiteName = re.search('www(.){1,20}com', str(pgLink))
        siteName = str(pgLink)[searchForSiteName.start():searchForSiteName.end()] #Gets domain name
        pageNum = ''
        lastChar = pgLink[len(pgLink)-1:]
        if (re.search(r'All', pgLink)):
            #if all inventory on one page return without modification to the url
            pageNum = 'All'
        elif (lastChar == "/"):
            #If the last character of the url is '/' then wan to remove it and then the page number
            pgLinkWOSlash = pgLink[:len(pgLink)-1]
            pageNum = pgLinkWOSlash[len(pgLinkWOSlash)-1:]
        elif (re.search(r'[0-9]$', lastChar)):
            #If the last character of the url is the page number then get it
            pageNum = pgLink[len(pgLink)-1:]
        else:
            pageNum = pgLink[len(pgLink)-1:]
            print('Error: Last Char not recognized in GetSiteNPageName()')
        return str(siteName+'Page'+str(pageNum))
        
    #Sets the dictionary keys of masterDictionary with each page link
    @staticmethod
    def CreateDictKeys(setOfPageLinks):
        allPages = {}
        #print('setOfPageLinks in CreateDictKeys(): ' + str(setOfPageLinks))
        for pgLink in setOfPageLinks:
            keyName = MainCrawlerClass.GetSiteNPageName(pgLink)
            allPages[keyName] = 'tempValue'
        return allPages
            
            
    def CrawlOnePage(self, threadName, inventoryUrlWNewPg):
        print('CrawlOnePage() called by : ' + str(threadName))
        html_text = MainCrawlerClass.GetHTMLText(inventoryUrlWNewPg)
        self.CheckIfPageBlocked(inventoryUrlWNewPg,html_text) 
        soup = BeautifulSoup(html_text, "lxml")
        #Will extract the html specific for each vehicle and put all of them for this single page in a list
        listOfInventoryVehiclesHTML = self.GetEachVehicleItemOnPage(soup)
        
        #Will put all vehicle info for each vehicle on this page into outputList
        outputList = self.GetAllVehicleInfoForPage(listOfInventoryVehiclesHTML)
        
        #Will cycle through the keys in the masterDictionary until it matches the page url
        #Hence the data we extracted will match the pageKey in the dictionary 
        for key in MainCrawlerClass.masterDictionary.keys():
            if str(key) == MainCrawlerClass.GetSiteNPageName(inventoryUrlWNewPg):
                MainCrawlerClass.masterDictionary[key] = outputList

    
    @staticmethod
    def SortMasterDictToOutputFiles(domainName1, domainName2, domainName3):
        MainCrawlerClass.UpdateQueueCrawledFiles()
        IOCls = InputOutputClass()
        #Orders the master list to that we can output in order of site and page number
        orderedMasterDict = coll.OrderedDict(sorted(MainCrawlerClass.masterDictionary.items()))

        listOfAllPagesDN1 = []
        listOfAllPagesDN2 = []
        listOfAllPagesDN3 = []
        
        #Categorizes the data into the relevant domain list
        for key in orderedMasterDict.keys():
            if re.search(str(domainName1), key):
                listOfAllPagesDN1.extend(orderedMasterDict[key])
            elif re.search(str(domainName2), key):
                listOfAllPagesDN2.extend(orderedMasterDict[key])
            elif re.search(str(domainName3), key):
                listOfAllPagesDN3.extend(orderedMasterDict[key])
            else: 
                print('Error: Cannot match key to domainNames in SortMasterDictToOutputFiles()')
        
        #Outputs txt files
        IOCls.WriteListIntoTabDelFile(str(domainName1 + '.txt'), listOfAllPagesDN1)
        IOCls.WriteListIntoTabDelFile(str(domainName2 + '.txt'), listOfAllPagesDN2)
        IOCls.WriteListIntoTabDelFile(str(domainName3 + '.txt'), listOfAllPagesDN3)
        print('Files Outputed!')
        
    @staticmethod   
    def GetHTMLText(url):
        html_text = ''
        try:
            source_code = req.get(url)
            html_text = source_code.text
        except:
            print('Error: Cannot Crawl Page, Check GetHTMLText()')
        return html_text
            
        
    @staticmethod
    def AddLinksToQueue(pageLinks):
        for pageUrl in pageLinks:
            if pageUrl in MainCrawlerClass.queueSet:
                continue
            if pageUrl in MainCrawlerClass.crawledSet:
                continue
            MainCrawlerClass.queueSet.add(pageUrl)
    
    
    @staticmethod
    def UpdateQueueCrawledFiles():
        IOCls = InputOutputClass()
        IOCls.SetToFile(MainCrawlerClass.queueSet, MainCrawlerClass.QUEUE_FILE)
        IOCls.SetToFile(MainCrawlerClass.crawledSet, MainCrawlerClass.CRAWLED_FILE)
    
        
    def GetAllVehicleInfoForPage(self, listOfInventoryVehiclesHTML):
        getSVInfoCls = GetSingleVehicleInfoClass()
        listOfAllVehicleInfoForPage =[]
        for vehicleHTML in listOfInventoryVehiclesHTML:
            #Takes vehicleHTML and extracts all info for that vehicle 
            listOfAllVehicleInfoForPage.append(getSVInfoCls.GetEachVehicleInfo(vehicleHTML))
        print('Output for page: ' + str(listOfAllVehicleInfoForPage))
        return listOfAllVehicleInfoForPage
        
        
    def GetUrlWOPgNum(self, inventoryUrlWPgNum):
        lastChar = inventoryUrlWPgNum[len(inventoryUrlWPgNum)-1:]
        if (re.search(r'All', inventoryUrlWPgNum)):
            #if all inventory on one page return without modification to the url
            return inventoryUrlWPgNum
        elif (lastChar == "/"):
            #If the last character of the url is '/' then wan to remove it and then the page number
            inventoryUrlWOSlash = inventoryUrlWPgNum[:len(inventoryUrlWPgNum)-1]
            inventoryUrlWOPgNum = inventoryUrlWOSlash[:len(inventoryUrlWOSlash)-1]
            return inventoryUrlWOPgNum
        elif (re.search(r'[0-9]$', lastChar)):
            #If the last character of the url is the page number then remove it
            inventoryUrlWOPgNum = inventoryUrlWPgNum[:len(inventoryUrlWPgNum)-1]
            return inventoryUrlWOPgNum
        else:
            inventoryUrlWOPgNum = inventoryUrlWPgNum[:len(inventoryUrlWPgNum)-1]
            return inventoryUrlWOPgNum
            
    
    def CheckIfPageBlocked(self, webPage, html_text):
        if re.search("Suspicious Activity", html_text):
            #Noticed that some web sites block you from using crawlers
            print ("Page blocked you: " + str(webPage))

        
    def CheckIfLastPage(self, soup, html_text):
        #If the site has a next page button then it is not the last page
        disabledSearch = soup.find_all('li', attrs= {'class': re.compile('disabled')})
        for tag in disabledSearch:
            seachNextinTag = re.search('Next', str(tag))
            if seachNextinTag:
                return True
          
        nextSearch = soup.find_all(string = re.compile('Next'))
        if nextSearch:
            return False
        else: 
            return True
    
    
    def GetEachVehicleItemOnPage(self, soup):
        listOfInventoryVehiclesHTML = []
        #Will search 'tr' & 'div' tags for these keywords which separates each vehicle on a page
        for item in soup.find_all('div',attrs={'class':re.compile("(row.srpVehicle)|(inventoryListItem)", re.IGNORECASE)}):
            listOfInventoryVehiclesHTML.append(item)
        return listOfInventoryVehiclesHTML
    
    
    
import csv
import os

class InputOutputClass:
   
    def WriteLinksFile(self, path, url):
        f = open(path, 'w')
        f.write(url)
        f.close
    
    def CreateProjectDir(self, directory):
        if not os.path.exists(directory):
            print('Creating project ' + directory)
            os.makedirs(directory)
            
    def CreateLinkFiles(self, projectName):
        queue = projectName + '/queue.txt'
        crawled = projectName + '/crawled.txt'
        self.ClearFileContents(queue)
        self.ClearFileContents(crawled)
        if not os.path.isfile(queue):
            self.WriteLinksFile(queue, '')
        if not os.path.isfile(crawled):
            self.WriteLinksFile(crawled, '')
            
    def FileToSet(self, filename):
        output = set()
        with open(filename, 'rt') as file:
            for line in file:
                output.add(line.replace('\n',''))
        return output
    
    def SetToFile(self, links, file):
        self.ClearFileContents(file)
        for link in links:
            self.AppendToFile(file, link)
        
    def AppendToFile(self, path, link):
        with open(path, 'a') as file:
            file.write(link + '\n')
    
    def ClearFileContents(self, path):
        with open(path, 'w'):
            pass
    
    def WriteListIntoTabDelFile(self, filename, listOfAllVehicleInfo):
        with open (filename,'w') as file:
            file.write('Unique ID\tMake\tModel\tTrim\tVIN\tColor\tMileage\tPrice\tImgUrl\n')
            file.writelines('\t'.join(i) + '\n' for i in listOfAllVehicleInfo)    
        
        
    #Some common ways of reading in tab delimited files
    #to check that the files I wrote are easily read back in
    def ReadTabDelFileManually(self, file):
        print('ReadTabDelFileManually: ')
        with open(file, 'r') as f:
            content = [x.strip().split('\t') for x in f]
            for vehicle in content:
                print(vehicle)
            return content
    
    
    def ReadTabDelFileCSV(self, file):
        print('ReadTabDelFileCSV:')
        readList =[]
        with open(file) as tsv:
            for line in csv.reader(tsv, dialect='excel-tab'): 
                print(line)
                readList.append(line)
        return readList
import re

class GetSingleVehicleInfoClass:

    #Creates list of all info for a single vehicle 
    #by taking in the html specific for that vehicle
    def GetEachVehicleInfo(self, vehicleHTML):
        listOfSingleCarInfo =[]
        listOfSingleCarInfo.append(self.GetIDNumber(vehicleHTML))
        listOfSingleCarInfo.extend(self.GetMakeModelTrim(vehicleHTML))
        listOfSingleCarInfo.append(self.GetVIN(vehicleHTML))
        listOfSingleCarInfo.append(self.GetColour(vehicleHTML))
        listOfSingleCarInfo.append(self.GetMileage(vehicleHTML))
        listOfSingleCarInfo.append(self.GetPrice(vehicleHTML))
        listOfSingleCarInfo.append(self.GetImgUrl(vehicleHTML))
        
        return listOfSingleCarInfo
    
    
    def GetIDNumber(self, vehicleHTML):
        selectorNameSearch = re.compile('(vehicle[0-9]{7}$)|(stockDisplay)') 
        cssSelectors = ['id','class']
        for cssSelector in cssSelectors:
            idSearch = vehicleHTML.find_all(['li','div'],attrs={cssSelector:selectorNameSearch})
            #Iterates through css selectors to identify which tag is where the ID Number is located
            #I also use regex to match the again this is using just the html of one specific vehicle
            for tag in idSearch:
                fullIdTag = tag.get('id')
                fullText = tag.get_text()
                if fullIdTag: 
                #If 'id' selector matched then I remove the 'vehicle' string
                #from the fullIdTag 'vehicle6094063' leaving just the ID number 
                    justNumIdTag = re.sub('[^0-9]+', '', fullIdTag)
                    return justNumIdTag
                elif fullText: 
                #If 'class' selector matched then I remove the 'Stock #:' string
                #from the fullTextTag 'Stock #: HHT821B' leaving just the ID number 
                    justStockId = fullText[9:]
                    return justStockId
                else:
                    #print('ID Number Identified, But Not isolated')
                    return ('N/A')
                #The return statements are setup in order to exit the function when 
                #the first match has been found and isolated
            
        print('ID Number Not Identified for either classes')
        return ('N/A') #Returns 'N/A' if cannot find match for either class or tag
            


    def GetMakeModelTrim(self, vehicleHTML):
        mMTSearch = vehicleHTML.find_all(string = re.compile('[1-2][0,9][0-9][0-9]'))
        if mMTSearch: #Looks for year of vehicle and will match '2014 Ford Taurus SEL'
            for tag in mMTSearch: 
                #Find at what Index of the string does the first word start
                findIndex = re.search('[A-Z]',tag)
                makeStartIndex = 6; #default start Index
                if findIndex:
                    makeStartIndex = findIndex.start()
                else: 
                    print('No Letter Found')
                
                makeModelTrim = tag[makeStartIndex:].split()
                #Then split the rest of the string by white space and
                #then categorize the words into Make, Model, and Trim 
                if len(makeModelTrim) == 2: 
                    makeModelTrim.extend(['N/A']) #Add Empty Trim if 3rd word does not exist
                    return makeModelTrim
                elif len(makeModelTrim) > 3:
                    #Anything after the 3rd element is considered part of Trim
                    makeModelTrim = makeModelTrim[:2] + [' '.join(makeModelTrim[2:])] 
                    return makeModelTrim
                elif len(makeModelTrim) < 1:
                    print('MakeModelTrim Identified, But Not Isolated')
                    return (['N/A','N/A','N/A'])
                elif len(makeModelTrim) == 1:
                    makeModelTrim.extend(['N/A']) #Add Empty Model
                    makeModelTrim.extend(['N/A']) #Add Empty Trim
                    return makeModelTrim
                elif len(makeModelTrim) == 3:
                    return makeModelTrim
                #Again the return statements are setup in order to exit the function when 
                #the first match has been found and categorized
        else: 
            print('MakeModelTrim Not Identified')
            return(['N/A'])
        
        
    def GetVIN(self, vehicleHTML):
        vinSearch = vehicleHTML.find_all(['label','strong'], string = re.compile('VIN'))
        #Searches 'label' & 'strong' tags for the string of VIN
        if vinSearch:
            for tag in vinSearch: 
                isolateVin= re.search('[A-Z0-9]{10,17}', str(tag.parent))
                #Matched for a 10-17 VIN Code using tag.parent to include the actual code
                #(have found VINs of 10 digits on sites, probably an error on their behalf)
                if isolateVin:
                    vinCode = str(tag.parent)[isolateVin.start():isolateVin.end()]
                else:
                    print('VIN Identified, but not isolated')
                    vinCode = str(tag.parent)
            return vinCode
        else: 
            #print('VIN Not Identified')
            return('N/A')
    
    
    def GetColour(self, vehicleHTML):
        colourSearch = vehicleHTML.find_all(['label','strong'], string = re.compile('Ext', re.IGNORECASE))
        #Search 'label' and 'strong' tags for a string that includes 'Ext' for 'Exterior Color'
        if colourSearch:
            for tag in colourSearch: 
                cleanParent = re.sub('Exterior|Ext|Color|extColor|li>|<li|label|span|strong|class','',str(tag.parent), 10, re.IGNORECASE)
                #Then remove essentially all words from the parent, even those from the tags and selectors
                isolateColour= re.search('([A-Za-z].)*[A-Za-z]{3,}(.[A-Za-z])*', str(cleanParent)) 
                #Then search the clean parent for a colour [A-Za-z]{3,} and any adjectives or elaborations before or after the colour 
                if isolateColour:
                    colour = str(cleanParent)[isolateColour.start():isolateColour.end()]
                    #Then cut the parent to isolate the colour
                else:
                    print('Colour Identified, but not isolated')
                    print('Colour tag.parent:' + str(tag.parent))
                    colour = str(tag.parent)
            return colour
        else: 
            #print('Colour Not Identified')
            return('N/A')
    
    
    def GetMileage(self, vehicleHTML):
        mileageSearch = vehicleHTML.find_all(['label','strong'], string = re.compile('Mileage:'))
        #Searched 'label' & 'strong' tags for the string 'Mileage:'
        if mileageSearch:
            for tag in mileageSearch: 
                isolateMileage= re.search('([0-9]){1,3}(,)?([0-9]){3}', str(tag.parent))
                #From the parent, it looks for a number between 1,000 & 999,999 with and without the comma
                if isolateMileage:
                    mileage = str(tag.parent)[isolateMileage.start():isolateMileage.end()]
                    #Then cut the parent to isolate the mileage
                else:
                    print('Mileage Identified, but not isolated')
                    print(str(tag.parent))
                    mileage = str(tag.parent)
            return mileage
        else: 
            #print('Mileage Not Identified')
            pass
        return('N/A')
    
    
    def GetPrice(self, vehicleHTML):
        isolatePrice = re.search('\$(.){1,8}[0-9]', str(vehicleHTML))
        #Searches for a string with $ sign then 1 to 8 numbers with perhaps a comma, then finishes with digit
        if isolatePrice:
            price = str(vehicleHTML)[isolatePrice.start():isolatePrice.end()]
            #Then cut the parent to isolate the mileage
            return price
        else:
            #print('Price Not Identified')
            price = 'N/A'
            return price
        
        
    def CheckIfStartWithHTTP(self, imgUrl, vehicleHTML):
        checkStartHttp = re.search('^http', imgUrl)
        #Check if imgUrl starts with http (which will also contain the base domain of the website
        if checkStartHttp:
            pass #If it does pass then simply return the imgUrl
        else:
            #If it doesn't search the the link (<a>) tags in vehicleHTML for the base domain 
            for tag in vehicleHTML.find_all('a',attrs={'href':re.compile('http://www(.){1,20}com')}):
                isolateStartHttp = re.search('http://www(.){1,20}com', str(tag))
                HttpStart = str(tag)[isolateStartHttp.start():isolateStartHttp.end()]
                imgUrl = HttpStart + imgUrl
                #Then isolate the base domain and add it to the start of imgUrl
                break #To stop it printing for all matches for the base domain
        return imgUrl
        
        
    def GetImgUrl(self, vehicleHTML):
        imgUrlSearch = vehicleHTML.find_all('img')
        #Search for the <img> tag
        if imgUrlSearch:
            for tag in imgUrlSearch:
                isolateImgUrl= re.search('src=(.)+(jpg|png)', str(tag.parent))
                #search parent of img tag for the source image url
                if isolateImgUrl:
                    imgUrl = str(tag.parent)[isolateImgUrl.start()+5:isolateImgUrl.end()]#Remove 'src='
                    imgUrl = self.CheckIfStartWithHTTP(imgUrl, vehicleHTML)#Add base domian 
                    return imgUrl
                else:
                    print('ImgUrl Identified, but not isolated')
                    imgUrl = str(tag)
                    return imgUrl
        else:
            #print('Image Not Identified')
            imgUrl = 'N/A'
            return imgUrl
        

    
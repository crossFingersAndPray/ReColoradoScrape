# -*- coding: utf-8 -*-
#import requests
#from bs4 import BeautifulSoup
#target_url = 'https://www.recolorado.com/find-real-estate/type-commercial/newestfirst-dorde'
#page = requests.get(target_url)
#soup = BeautifulSoup(page.content,'html.parser')
#print(soup.prettify())
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

def getIndividualListingUrlsFromSearchPage(driver,search_page_url):
    list_of_urls = []
    driver.get(search_page_url)
    h1loc = driver.find_element_by_class_name('photo-results')
    h2loc = h1loc.find_element_by_xpath("//div[@class='results results__photo']")
    list_of_listings_we = h2loc.find_elements_by_xpath("//*[@class='results--item results--item__photo']")
    for l_we in list_of_listings_we:
        listing_deets = l_we.find_element_by_xpath('.//section[@class="listing listing__photo"]')
        url = listing_deets.find_element_by_xpath('.//a[@class="listing--media listing--media__photo"]').get_attribute('href')
        list_of_urls.append(url)
    return list_of_urls

#workbook = Workbook()
outputPath = "C:\\Users\Public\\Desktop\\reColoradoAgregate.xlsx"
base_url = 'https://www.recolorado.com/find-real-estate/type-commercial/%d-pg/exclusive-dorder/newestfirst-dorder/photo-tab/'
max_lookback_date = datetime(2019,1,1)
num_of_retries = 2
#workbook.save(outputPath)
column_names = ['status', 'listed on', 'street Address', 'city', 'state', 'zip', 'listingID', 'latitude', 'longitude', 'price', 
                              'sqft', 'bedrooms', 'bathrooms', 'MLS Number', 'isExclusive', 'isHomeValue',
                              'Listing Status ID', 'Year Built', 'Lot Size', 'date of last price change', 'percent reduced', 'dollar amount reduced', 'url']

df = pd.DataFrame(columns = column_names)

#base_url = 'https://www.recolorado.com/find-real-estate/type-commercial/from-268000/to-290000/%d-pg/exclusive-dorder/newestfirst-dorder/photo-tab/'
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = "C:/Users/jaafari/Desktop/chromedriver.exe"
driver = webdriver.Chrome(options=options,executable_path=DRIVER_PATH)

driver.get(base_url%1)

number_of_pages = int(driver.find_element_by_class_name('pagination').get_attribute('data-pages'))

#listing_class = "/ol[@class='results--list results--list__photo']"
list_of_urls = []
for page_num in range(1,number_of_pages+1):
    search_page_url = base_url%page_num
    for i in range(10):
        try:
           list_of_urls = list_of_urls + getIndividualListingUrlsFromSearchPage(driver, search_page_url)
           break
        except Exception:
            driver.close
            continue

subDriver = webdriver.Chrome(options=options,executable_path=DRIVER_PATH)
output = []
failed_urls = []
num_url = len(list_of_urls)
count = 1
for url in list_of_urls:
    isSuccessfulParse = False
    for i in range(num_of_retries):
        try:
            subDriver.get(url)
            basic_info = subDriver.find_element_by_xpath("//main[@class='page--body']/div[@class='page--full']/div/section[@class='listing listing__heading listing']/div[@class='listing--information listing--information__heading']/div[@class='listing--location listing--location__heading']/div[@class='hide']")
            streetAddress = basic_info.find_element_by_xpath("./span[@hmsitemprop='streetAddress']").get_attribute('innerHTML')
            city = basic_info.find_element_by_xpath("./span[@hmsitemprop='addressLocality']").get_attribute('innerHTML')
            state = basic_info.find_element_by_xpath("./span[@hmsitemprop='addressRegion']").get_attribute('innerHTML')
            zipCode = basic_info.find_element_by_xpath("./span[@hmsitemprop='postalCode']").get_attribute('innerHTML')
            listingID = basic_info.find_element_by_xpath("./span[@hmsitemprop='ListingID']").get_attribute('innerHTML')
            latitude = basic_info.find_element_by_xpath("./span[@hmsitemprop='Latitude']").get_attribute('innerHTML')
            longitude = basic_info.find_element_by_xpath("./span[@hmsitemprop='Longitude']").get_attribute('innerHTML')
            price = basic_info.find_element_by_xpath("./span[@hmsitemprop='Price']").get_attribute('innerHTML')
            sqrft = basic_info.find_element_by_xpath("./span[@hmsitemprop='SearchableSqft']").get_attribute('innerHTML')
            bedrooms = basic_info.find_element_by_xpath("./span[@hmsitemprop='Bedrooms']").get_attribute('innerHTML')
            bathrooms = basic_info.find_element_by_xpath("./span[@hmsitemprop='Bathrooms']").get_attribute('innerHTML')
            mlsNumber = basic_info.find_element_by_xpath("./span[@hmsitemprop='MlsNumber']").get_attribute('innerHTML')
            isExclusive = basic_info.find_element_by_xpath("./span[@hmsitemprop='Exclusive']").get_attribute('innerHTML')
            isHomeValue = basic_info.find_element_by_xpath("./span[@hmsitemprop='IsHomeValue']").get_attribute('innerHTML')
            listingStatusID = basic_info.find_element_by_xpath("./span[@hmsitemprop='ListingStatusID']").get_attribute('innerHTML')
            yearBuilt = basic_info.find_element_by_xpath("./span[@hmsitemprop='YearBuilt']").get_attribute('innerHTML')
            lotSize = basic_info.find_element_by_xpath("./span[@hmsitemprop='LotSize']").get_attribute('innerHTML')
            
            listing_content = subDriver.find_element_by_xpath("//main[@class='page--body']/div[@class='page--full']/div/div[@class='main-content']/div[@class='page--column page--column__listing']")
            #/div[@class='listing--information__tertiaryinfo-desk page--column__primary']/ol/li
            status_div = listing_content.find_element_by_xpath("./section[@class='section-container container--pane listing--information__contain']/div[@class='listing--information listing--information__primaryinfo page--column__secondary']/div[@class='listing--address__mobile listing--address__heading']/span[@class='listing--status__active-mobile listing--status__active']")
            status_raw = status_div.get_attribute('innerHTML')
            listed_on_raw = listing_content.find_element_by_xpath(".//section[@class='section-container container--pane listing--information__contain']/div[@class='listing--information listing--information__primaryinfo page--column__secondary']/div[@class='listing--information__tertiaryinfo-mobile page--column__primary  ']/ol/li").get_attribute('innerHTML')
            
            status = status_raw.split('\n')[0]
            listed_on = listed_on_raw.split('</span>')[-1].strip()
            
            
            try:
                history_div = listing_content.find_element_by_id('js-price-history')
                if history_div is not None:
                    history_rows = history_div.find_elements_by_xpath('./div[@class="container--pane container--pane__pricehistory"]/section[@class="pricehistory--body pricehistory--body__page"]/div[@class="table table__pricehistory"]/div[position()=2]/*[@class="table--row table--row__pricehistory table--row__body"]')
                    row = history_rows[0]
                    dateChange = row.find_element_by_xpath('./li[@class="table--field table--field__pricehistory table--field__body"][position()=1]').text
                    dateChange = datetime.strptime(dateChange,'%m/%d/%Y')
                    
                    change_cell = row.find_element_by_xpath('./li[@class="table--field table--field__pricehistory table--field__body"][position()=4]').text
                    change_split = change_cell.split('-')
                    if len(change_split) == 1:
                        print('not sure why the price history split did not work. check out this url: ' + url)
                        failed_urls.append(url)
                    
                    change_dollar_amt = change_split[0]
                    change_percentage = '-'+change_split[1]
            except NoSuchElementException:
                history = []
                dateChange = datetime(2000,1,1)
                change_dollar_amt = '$0'
                change_percentage = '0%'
            listing_data_struct=[status, datetime.strptime(listed_on,'%m/%d/%y'), streetAddress, city, state, zipCode, listingID, latitude, longitude, price, 
                             sqrft, bedrooms, 
                     bathrooms, mlsNumber, isExclusive, isHomeValue, listingStatusID, yearBuilt, lotSize, dateChange, change_percentage, change_dollar_amt, url]

            output.append(listing_data_struct)
            print('completed url %d out of %d'%(count,num_url))
            count+=1
            isSuccessfulParse  = True
            break
        except Exception:
            continue
    if isSuccessfulParse == False:
        print('Unable to parse the following url: ' + url)
        count+=1
    elif datetime.strptime(listed_on,'%m/%d/%y') < max_lookback_date:
        break
subDriver.quit()
driver.quit()
df = pd.DataFrame(output,columns=column_names)
df['listed on'] = df['listed on'].astype('datetime64[ns]')
df['date of last price change'] = df['date of last price change'].astype('datetime64[ns]')
writer = pd.ExcelWriter(outputPath, date_format='yyyy/mm/dd')
df.to_excel(outputPath)
print('These are the failed urls: ')
print(failed_urls)

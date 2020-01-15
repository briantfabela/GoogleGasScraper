# Python 3.7.1 - Briant J. Fabela (12/26/2019)

from selenium import webdriver # selenium v3.141.0

# for 'explicit' wait implementation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from os import path


def read_addresses(txt_file_path):
    '''Returns a text file of addresses as a python list'''

    addresses = open(txt_file_path) # file should have an address per line
    return [line.strip('\n') for line in addresses] # returns addresses as list

def get_latlong(url):
    '''Returns dict of latitude & longitude from a location in google maps'''

    x, y = url.split('/@')[1].split('/data=!')[0].split(',')[:2]
    return GeoInfo(x, y)

class GeoInfo:
    '''Stores geographical data about a location visisted on google maps'''

    def __init__(self, x, y):
        self.lat = float(x)
        self.long = float(y)

class GasPriceChecker:
    '''Uses the selenium driver to visit a list of gas station addresses'''

    def __init__(self, url, xpaths, addresses_txt_file_path):
        self.url = url
        self.xpaths = xpaths # xpath dictionary
        self.locations = read_addresses(addresses_txt_file_path)
        self.driver_fp = r'chromedriver_win32/chromedriver_v79.exe'
    
    def check(self, max_window=True, dims=(1080,800)):
        '''Opens the webridriver using Selenium.

        After opening the driver it begins parsing thru self.locations and
        scraping the gas price text from the side bar.
        '''

        self.driver = webdriver.Chrome(self.driver_fp)

        # set window size and go to url
        if max_window: 
            self.driver.maximize_window()
        else:
            self.driver.set_window_size(*dims)
        self.driver.get(self.url)

        for loc in self.locations:
            # lets shorten self.driver.find_element_by_xpath
            find_by_xpath = self.driver.find_element_by_xpath
            field = find_by_xpath(self.xpaths['searchField'])
            field.send_keys(loc) # type in location

            field_button = find_by_xpath(self.xpaths['searchButton'])
            field_button.click() # click search button

            # Lets catch search results screen if it appears
            if len(self.driver.current_url) < 80:
                print('Possible Search Results Screen')
                sleep(3) # allow search results to load
                # click on first result
                try:
                    # usually this is the right xpath
                    find_by_xpath(self.xpaths['searchResult1']).click()
                except:
                    # fallback
                    find_by_xpath(self.xpaths['searchResult2']).click()

            '''
            wait = WebDriverWait(self.driver, 10).until( # wait until the streetview loads
                EC.visibility_of_element_located((By.XPATH, self.xpaths['titleCard']))
            )

            # get lat and long; print to console
            latlong = get_latlong(self.driver.current_url)
            print("lat: {} long: {}".format(latlong.lat, latlong.long))'''

            back_button = find_by_xpath(self.xpaths['backButton'])
            back_button.click() # click back button

            wait = WebDriverWait(self.driver, 10).until( # searchField needs some time to load
                EC.visibility_of_element_located((By.XPATH, self.xpaths['searchField']))
            )

            field.clear()

        print("Tour has ended.")
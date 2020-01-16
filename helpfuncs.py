# Python 3.7.1 - Briant J. Fabela (12/26/2019)

from selenium import webdriver # selenium v3.141.0

# for 'explicit' wait implementation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Selenium exception handling
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from datetime import datetime
from time import ctime

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

class GasPrices:
    '''Stores fuel prices as scraped from google maps'''

    def __init__(self, diesel, reg, mid, premium):
        self.diesel = diesel
        self.regular = reg
        self.midgrade = mid
        self.premium = premium
        # timestamp will be in local time (MST for me)
        self.timestamp = ctime(datetime.now().timestamp())

class GasPriceChecker:
    '''Uses the selenium driver to visit a list of gas station addresses'''

    def __init__(self, url, xpaths, addresses_txt_file_path):
        self.url = url
        self.xpaths = xpaths # xpath dictionary
        self.locations = read_addresses(addresses_txt_file_path)
        self.driver_fp = r'chromedriver_win32/chromedriver_v79.exe'

    def parse_prices(self, string):
        '''Parses thru prices string and returns a GasPrices instance'''

        return GasPrices(
            *[i.strip('$') for i in string.split() if '$' in i or '-' in i]
        )
    
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
            # shorten self.driver.find_element_by_xpath
            find_by_xpath = self.driver.find_element_by_xpath
            field = find_by_xpath(self.xpaths['searchField'])
            field.send_keys(loc) # type in location

            field_button = find_by_xpath(self.xpaths['searchButton'])
            field_button.click() # click search button
    
            try:
                # wait for element to be visible
                wait = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, 'section-gas-prices-container')
                    )
                )

                # get prices
                raw_prices = self.driver.find_element_by_class_name(
                'section-gas-prices-container').text

                # parse and assign
                self.prices = self.parse_prices(raw_prices)
                # get coordinates
                self.geo = get_latlong(self.driver.current_url)

                # print all the info
                print(loc, 
                "Coords: "+str(self.geo.lat)+", "+str(self.geo.long),
                "Disl: "+self.prices.diesel, 
                "Regl: "+self.prices.regular,
                "Midg: "+self.prices.midgrade,
                "Perm: "+self.prices.premium, sep='\n')
    
            except TimeoutException:
                print("TimeoutException")
                print(loc, "passed.")
                pass

            except NoSuchElementException:
                print("NoSuchElementException")
                print(loc, "passed.")
                pass

            field.clear()

        print("Tour has ended.")

# test code
def main():
    xpaths = dict(
        searchField = '//*[@id="searchboxinput"]',
        searchButton = '//*[@id="searchbox-searchbutton"]'
    )
    
    x = GasPriceChecker('https://www.google.com/maps', xpaths, 'gas_stations.txt')
    x.check()

if __name__ == "__main__":
    main()
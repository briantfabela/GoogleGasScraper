# Python 3.7.1 - Briant J. Fabela (1/15/2020)

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
import os
import csv

def read_addresses(txt_file_path) -> []:
    '''Returns a text file of addresses as a python list'''

    addresses = open(txt_file_path) # file should have an address per line
    return [line.strip('\n') for line in addresses] # returns addresses as list

def get_latlong(url):
    '''Returns dict of latitude & longitude from a location in google maps'''

    x, y = url.split('/@')[1].split('/data=!')[0].split(',')[:2]
    return GeoInfo(x, y)

def make_nested_folders(path):
    """
    Creates all of the non-existent directories in a relative path from cwd.

    If any directories already exist they are skipped and not overwritten.
    
    Args:
        path (str): relative file path of non-existent subfolders folders.
    """

    # check for minimal length and str type
    if len(path) < 0 or not isinstance(path, str):
        print("path needs to be a string of character length 1 or longer.")
        return

    dir_path = os.path.normpath(path) # normalize path
    folder_list = dir_path.split(os.sep) # create list of folders in nested order
    path_string = ''

    for folder in folder_list:

        # update path and normalize
        if len(path_string) is 0:
            path_string += folder
        else: # if not first directory in path_string add separator
            path_string += "\\" + folder

        path_string = os.path.normpath(path_string)

        if os.path.isdir(path_string): # does the directory exist
            print(path_string, 'already exists.')
            pass
        else:
            os.mkdir(path_string) # if not create it
            print(path_string, "created.")

def create_csv(file_path, name):
    """
    Creates csv file at a nested subfolder folder path.

    It also creates any folders in that path if they do not exist.
    
    Args:
        file_path (str): Relative file path from cwd
        name (str): Name of file including '.csv'
    """

    if not os.path.isdir(file_path): # if the directory does not exist
        print("Directory does not exist")
        make_nested_folders(file_path)
        print(file_path, "created")

    if not os.path.isfile(os.path.join(file_path, name)): # dir exists but not file
        with open(os.path.join(file_path, name), 'w', newline='') as empty_csv:
            pass
        print(name, "created.")

    else: # dir and file exist
        print(name, "already exists.")

def make_file_structure(zipcode, fp='fuel_prices'):
    """
    Generates a file structure and csv files for fuel types to store price info

    Also creates an empty '_gas_stations_{'zipcode'}.txt' file.
    
    Args:
        zipcode (str): 5-digit number string of a valid U.S. zip code
        fp (str): Directory where zipcode folders are stored. 
    """

    # create fuelprices/{zipcode} along with fueltype .csv files, with headers
    path = os.path.join(fp, zipcode)

    for fuel_type in ['diesel', 'regular', 'midgrade', 'premium']:
        create_csv(path, fuel_type+'.csv')

    # create empty _gas_stations_{'zipcode'}.txt
    open(os.path.join(path, "_gas_stations_"+zipcode+".txt"), 'a').close()

def populate_gas_stations(stations=20, fp='fuel_prices'):
    """
    Populates '_gas_stations_{zipcode}.txt' files in each zipcode folder inside
    the root fp directory; dfault named 'fuel_prices'

    Gas stations populated had fuel price information at the time of scraping

    Gas stations addresses are saved in the following convention: 
    {name}, {address}, {city}, {state} {zipcode}
    
    Args:
        stations (int, optional): number of stations wanted. Defaults to 20.
        fp (str, optional): directory of where zipcode folders are populated
    """

    # TODO: iterate through 'fuel_prices' or equivalent, zipcode folders
    # TODO: scrape 
    pass

class GeoInfo:
    '''Stores geographical data about a location visisted on google maps'''

    def __init__(self, x, y):
        self.lat = float(x)
        self.lon = float(y)

class GasPrices:
    '''Stores fuel prices as scraped from google maps'''

    def __init__(self, diesel, reg, mid, premium):
        self.diesel = diesel
        self.regular = reg
        self.midgrade = mid
        self.premium = premium
        # timestamp will be in local time
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
                "Coords: "+str(self.geo.lat)+", "+str(self.geo.lon),
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
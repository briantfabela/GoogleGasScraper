# Python 3.7.1 - Briant J. Fabela (1/15/2020)

from selenium import webdriver # selenium v3.141.0

# for 'explicit' wait implementation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Selenium exception handling
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException

from datetime import datetime
from time import ctime, sleep
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
    # if it exists it will not be modified
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
    #       get all the _gas_stations_{'zipcode'}.txt file paths
    # TODO: scrape per zipcode
    # TODO: write results to each zipcode's gas station txt file
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

    xpaths = dict(
        searchField = '//*[@id="searchboxinput"]',
        searchButton = '//*[@id="searchbox-searchbutton"]'
    )

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

class GasStation:

    def __init__(self):
        """
        Stores information for gas station results as they are being scraped
        """

        self.has_prices = True # default; will change while scraping if True

class GasStationScraper:

    def __init__(self, txt_fp, zipcode, stations=20):
        """
        Uses selenium to scrape gas station addresses in and around a zip code
        in Google Maps.
        
        Args:
            fp (str): file path of '_gas_stations_{zipcode}.txt' file.
            zipcode ([type]): ZIP code from which stations will be scraped.
            stations (int, optional): number of stations to be scraped.
        """

        self.url = 'https://www.google.com/maps'
        self.xpaths = dict(
            searchField = '//*[@id="searchboxinput"]',
            searchButton = '//*[@id="searchbox-searchbutton"]'
        )
        self.gas_txt_fp = txt_fp # relative path '_gas_stations_{zipcode}.txt'
        self.driver_fp = r'chromedriver_win32/chromedriver_v79.exe'
        self.scrape_depth = stations # how many stations to scrape in total
        self.zipcode = zipcode
    
    def find_and_click_field(self, field_xpath, button_xpath, field_input, clear=False):
        """
        Finds field element, sends keys, and clicks the search button
        
        Args:
            field_xpath (str): XPATH for input field elements.
            button_xpath (str): XPATH for search button element.
            field_input (str): Text that will be typed into search field.
            clear (bool): Wait for searchfield to be clickable and clear it.
        """

        find_by_xpath = self.driver.find_element_by_xpath # shorten func call
        field = find_by_xpath(field_xpath)

        if clear: # wait and clear field
            wait = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, self.xpaths['searchField'])
                )
            )
            field.clear()

        field.send_keys(field_input)
        
        button = find_by_xpath(button_xpath)
        button.click()

    def init_driver(self, max_window, dims):
        """
        Initializes the driver and sets window parameters.
        
        Args:
            max_window (bool): [description]
            dims (tuple): Window dimensions if not max_window
        """
        self.driver = webdriver.Chrome(self.driver_fp) # open web browser

        # set window size
        if max_window: 
            self.driver.maximize_window()
        else:
            self.driver.set_window_size(*dims)

        # go to url
        self.driver.get(self.url)

    def get_results(self):
        """
        Scrapes and parses gas stations search results until self.scrape_depth
        is reached and returns a list of the results as GasStation Objects.

        Returns:
            lst: returns GasStation objects with name and st address data
        """

        wait = WebDriverWait(self.driver, 3).until(
            EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'section-result')
            )
        )

        scraped_stations = []
        gas_stations = self.driver.find_elements_by_class_name('section-result')

        while len(scraped_stations) < self.scrape_depth:

            gas_stations = self.driver.find_elements_by_class_name(
                'section-result'
            )

            for result_index, station in enumerate(gas_stations):
                print("result_index:", result_index)
                find_class_name = station.find_element_by_class_name
                biz_name = find_class_name('section-result-title').text

                try: # if prices element is present
                    find_class_name('section-result-annotation')
                except NoSuchElementException:
                    print(biz_name, "has no fuel price information available.")
                else:
                    gs = GasStation()
                    gs.name = biz_name
                    gs.st_ad = find_class_name('section-result-location').text
                    scraped_stations.append(gs)

                if len(scraped_stations) == self.scrape_depth:
                    break

                if result_index == len(gas_stations) - 1:
                    print("Next Page.")
                    self.next_page()

        return scraped_stations

    def next_page(self):
        '''Click the 'Next Page on Google Maps search results page.'''

        try:
            next_button = self.driver.find_element_by_xpath(
                '//*[@id="n7lv7yjyC35__section-pagination-button-next"]'
            ) # click 'next' button for 2nd page of gas station results
            next_button.click()
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Last Page Reached?")
            pass
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException: Last Page Reached?")
            pass
        else:
            sleep(2.1)

    def add_gas_station(self, name, address):
        """
        Using the scraped name and address information it adds the gas station
        as a new line in the '_gas_stations_{zipcode}.txt' file.

        Text file entry convention:
        {Biz name}, {#} {Street}, {City}, {State} {ZIP code}
        
        Args:
            name (str): Business name of the gas station.
            address ([type]): Full address including city, state and zipcode.
        """

        pass

    #TODO: reconsider just scraping the station name and street address from results page
    #      then search these out through the search bar and individually instead of iterating
    #      through a url which may change

    def scrape_results(self, max_window=True, dims=(800,800)):
        """
        Iterates through the results page and saves the name and street address
        
        Args:
            max_window (bool, optional): Maximize window. Defaults to True.
            dims (tuple, optional): Window dimensions. Defaults to (800,800).
        """
        self.init_driver(max_window, dims) # start driver to url and set window

        for search in [self.zipcode, 'gas stations']: # search for zip and gas
            self.find_and_click_field(
                self.xpaths['searchField'],
                self.xpaths['searchButton'],
                search,
                True # wait and clear the search field
            )

        self.gs_list = self.get_results() # gas station list

        # and get full address
        # TODO: sometimes during multi-page scraping ads will make duplicates
        for g in self.gs_list:
            self.find_and_click_field(
                self.xpaths['searchField'],
                '//*[@id="searchbox-searchbutton"]',
                ' '.join([g.name, g.st_ad]), # concactenate name and st address
                True
            )
            try:
                wait = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_all_elements_located(
                        (By.CLASS_NAME, 'section-info-line')
                    ) # wait for info to load in sidebar
                )
            except TimeoutException:
                # in case of multiple results, click the first top one
                try:
                    # usually this is the right xpath
                    self.driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[1]'
                    ).click()
                except:
                    # sometimes the above xpath does not work
                    self.driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]'
                    ).click()
                finally:
                    wait = WebDriverWait(self.driver, 2).until(
                        EC.visibility_of_all_elements_located(
                            (By.CLASS_NAME, 'section-info-line')
                        ) # wait for info to load in sidebar
                    )

            g.address = self.driver.find_element_by_class_name(
                'section-info-line'
            ).text # get full address

        # debug
        for g in self.gs_list:
            print(g.name, g.address)
        




    def scrape(self, max_window=True, dims=(1000,800)):
        """
        After opening the driver it begins parsing thru 'gas staion' search
        results after a ZIP code search. It idenitified gas stations with fuel
        price data and begins scraping their name and address, and then
        ppulates the '_gas_stations_{zipcode}.txt' file.
        '''
        
        Args:
            max_window (bool, optional): Maximize window. Defaults to True.
            dims (tuple, optional): Window dimensions. Defaults to (1080,800).
        """
        self.driver = webdriver.Chrome(self.driver_fp) # open web browser

        # set window size
        if max_window: 
            self.driver.maximize_window()
        else:
            self.driver.set_window_size(*dims)

        # go to url
        self.driver.get(self.url)

        # do zip code search
        find_by_xpath = self.driver.find_element_by_xpath # shorten func call
        field = find_by_xpath(self.xpaths['searchField'])
        field.send_keys(self.zipcode) # type in zipcode

        field_button = find_by_xpath(self.xpaths['searchButton'])
        field_button.click() # click search button

        # wait for search field to be interactable before clearing field
        wait = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable(
                (By.XPATH, self.xpaths['searchField'])
            )
        )

        # do gas stations search
        field.clear()
        field.send_keys('gas stations')
        field_button.click()

        scraped_stations = [] # store the stations with fuel price information

        wait = WebDriverWait(self.driver, 6).until( # wait for full url to load
            EC.url_contains("data=!3m1!4b1")
        )

        # search results url
        results_page_url = self.driver.current_url

        while len(scraped_stations) < self.scrape_depth:

            # wait for 'section-result' elements to load before scraping
            wait = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, 'section-result')
                )
            )

            gas_stations = self.driver.find_elements_by_class_name(
                'section-result' # get all section results
            )

            for i in range(len(gas_stations)):

                # shorten call
                find_class_name = gas_stations[i].find_element_by_class_name
                # get gas station name for debugging
                station_name = find_class_name('section-result-title').text

                try: # check for gas price availability
                    has_info = find_class_name('section-result-annotation')
                    gs = GasStation()
                    gas_stations[i].click()

                    # wait for address info to load
                    wait = WebDriverWait(self.driver, 2).until(
                        EC.visibility_of_all_elements_located(
                            (By.CLASS_NAME, 'section-info-line')
                        )
                    )

                    gs.name = station_name

                    gs.address = self.driver.find_elements_by_class_name(
                        'section-info-line'
                    )[0].text # gas station full address

                    gs.url = self.driver.current_url # url for gas station

                    scraped_stations.append(gs) # add GasStation to list

                    #debug
                    print(gs.name, gs.address, gs.has_prices)

                    self.driver.get(results_page_url)

                    wait = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_all_elements_located(
                            (By.CLASS_NAME, 'section-result')
                        )
                    )
                    
                    gas_stations = self.driver.find_elements_by_class_name(
                        'section-result' # get all section results
                    )

                except ElementClickInterceptedException:
                    print("ElementClickInterceptedException: @ has_info")
                    pass
                except NoSuchElementException: # no gas prices found in element
                    print("NoSuchElementException @ has_info for:", station_name)
                    pass
                except StaleElementReferenceException: # element not found
                    print("StaleElementReferenceException @ has_info")
                    pass

                # when the amount of stations with fuel price wanted
                if len(scraped_stations) == self.scrape_depth:
                    break

            try:
                if len(scraped_stations) == self.scrape_depth: # skip
                    break

                next_button = self.driver.find_element_by_xpath(
                    '//*[@id="n7lv7yjyC35__section-pagination-button-next"]'
                ) # click 'next' button for 2nd page of gas station results
                next_button.click()

                wait = WebDriverWait(self.driver, 6).until( # wait for full url to load
                    EC.url_contains("data=!3m1!4b1")
                )

                results_page_url = self.driver.current_url # search results url

            except NoSuchElementException:
                print("NoSuchElementException: Last Page Reached.")
                break
            except StaleElementReferenceException:
                print("StaleElementReferenceException: Last Page Reached.")
                break
            except ElementClickInterceptedException:
                print("ElementClickInterceptedException: Last Page Reached.")
                break
        
        # after reaching scape_depth write gas stations addresses to text file
        print("gs list length:", len(scraped_stations))


''' dir() of:
<class 'selenium.webdriver.remote.webelement.WebElement'>
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', 
'__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', 
'__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_execute', '_id', '_parent', '_upload', 
'_w3c', 'clear', 'click', 'find_element', 'find_element_by_class_name', 'find_element_by_css_selector', 
'find_element_by_id', 'find_element_by_link_text', 'find_element_by_name', 
'find_element_by_partial_link_text', 'find_element_by_tag_name', 'find_element_by_xpath', 
'find_elements', 'find_elements_by_class_name', 'find_elements_by_css_selector', 'find_elements_by_id', 
'find_elements_by_link_text', 'find_elements_by_name', 'find_elements_by_partial_link_text', 
'find_elements_by_tag_name', 'find_elements_by_xpath', 'get_attribute', 'get_property', 'id', 
'is_displayed', 'is_enabled', 'is_selected', 'location', 'location_once_scrolled_into_view', 'parent', 
'rect', 'screenshot', 'screenshot_as_base64', 'screenshot_as_png', 'send_keys', 'size', 'submit', 
'tag_name', 'text', 'value_of_css_property']
'''
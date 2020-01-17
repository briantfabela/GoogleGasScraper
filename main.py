# Python 3.7.1 - Briant J. Fabela (12/26/2019)

from selenium import webdriver # selenium v3.141.0

# for 'explicit' wait implementation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import helpfuncs
import os

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
    path_list = dir_path.split(os.sep) # create list of folders in nested order
    path_string = path_list[0] # initialize the first folder in our path

    for i in range(len(path_list)):
        while os.path.isdir(path_string):
            print("")
        #TODO: use enumerate to use a for loop and access indexes in path_list

        '''
        if os.path.isdir(path_string):
            if i == len(path_list) - 1: # check if current loop is last index
                print("boop!")
                pass
            else:
                print(path_string, "already exists")
                path_string += "/" + path_list[i+1]
                path_string = os.path.normpath(path_string)
                print(path_string)
        else:
            os.mkdir(path_string)

            if i == len(path_list) - 1:
                pass
            else:
                path_list += "/" + path_list[i+1]
        '''

            


make_nested_folders('folder/subfolder/another_folder/final_folder')
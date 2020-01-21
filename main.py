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
            os.mkdir(path_string)
            print(path_string, "created.")

        

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
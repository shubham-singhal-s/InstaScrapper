"""
Hey Everyone!
This program can be used to scrape photos from any Instagram account (Offcourse, only if you follow that account or it’s an open account) and write the photo description for each photo to Excel Sheet.
"""
__author__ = "Darshan Majithiya"
__email__ = "darsh2115@gmail.com"

import time
import traceback
from time import sleep
import sys
import os
import shutil
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# from xlsxwriter import Workbook


class Scraper:
    def initBrowser(self, options):
        try:
            driver = webdriver.Chrome(
                "chromedriver_windows32/chromedriver.exe", chrome_options=options
            )  # I'm using linux. You can change it as per your OS.
            self.main_url = "https://www.instagram.com"
        except Exception as e:
            print(e)
        # check the internet connection and if the home page is fully loaded or not.
        try:
            driver.get(self.main_url)

        except TimeoutError:
            print(
                "Loading took too much time. Please check your connection and try again."
            )
            sys.exit()
        return driver

    def __init__(self, username, password, target_username, nOfPosts):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.image_list = []
        self.lastHeight = 0
        self.base_path = os.path.join(
            "data", self.target_username
        )  # change it as per requirement
        self.imagesData_path = os.path.join(
            self.base_path, "images"
        )  # change it as per requirement
        self.descriptionsData_path = os.path.join(
            self.base_path, "descriptions"
        )  # change it as per requirement
        self.no_of_posts = nOfPosts
        print(self.no_of_posts)
        options = Options()

        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        self.driver = self.initBrowser(options)

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "loginForm"))
            )
        except Exception as e:
            print(e)

        self.login()
        # self.close_dialog_box()
        self.open_target_profile()
        # # check if the directory to store data exists
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
        if not os.path.exists(self.imagesData_path):
            os.mkdir(self.imagesData_path)
        if not os.path.exists(self.descriptionsData_path):
            os.mkdir(self.descriptionsData_path)
        self.download_posts()

        self.driver.close()

    def login(self):
        try:
            username_input = self.driver.find_element_by_xpath(
                '//input[@name = "username"]'
            )
            username_input.send_keys(self.username)
        except Exception as e:
            print("Unable to find the username field.", e)
            sys.exit()

        try:
            password_input = self.driver.find_element_by_xpath(
                '//input[@name = "password"]'
            )
            password_input.send_keys(self.password)
        except Exception as e:
            print("Unable to find the password field.", e)
            sys.exit()

        try:
            time.sleep(1)
            login_link = self.driver.find_element_by_xpath('//div[text()="Log In"]')
            login_link.click()
        except Exception:
            print("Unable to find the Login button.")
            sys.exit()

        # check if the login page is fully loaded or not.

        print("Logging in...")

        # check if the login was successful
        try:
            WebDriverWait(self.driver, 10).until(EC.title_is("Instagram"))
        except Exception:
            print("Please try again with correct credentials or check your connection.")
            sys.exit()

        print("Login Successful!")

    def close_dialog_box(self):
        """ Close the Notification Dialog """
        try:
            time.sleep(3)
            close_btn = self.driver.find_element_by_xpath('//button[text()="Not Now"]')
            close_btn.click()
        except Exception:
            pass

    def open_target_profile(self):
        target_profile_url = (
            self.main_url + "/explore/tags/" + self.target_username
        )  # /explore/tags
        print("Redirecting to {0} profile...".format(self.target_username))

        # check if the target user profile is loaded.
        try:
            self.driver.get(target_profile_url)
            WebDriverWait(self.driver, 10).until(
                EC.title_contains(self.target_username)
            )

            soup = BeautifulSoup(self.driver.page_source, "lxml")
            counts = soup.find_all("span")
            counts = [c for c in counts if "," in c]
            print(counts)

        except Exception as e:
            traceback.print_exc()
            print(
                "Some error occurred while trying to load the target username profile.",
                e,
            )
            sys.exit()

    def extractImages(self):
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        all_images = soup.find_all("img", attrs={"style": "object-fit: cover;"})
        for img in all_images:
            if img not in self.image_list:
                self.image_list.append(img)
        print("Loaded {} images.".format(len(self.image_list)))

    def getPageHeight(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    def loadMore(self):
        """Scroll down and wait till new posts load"""
        currentHeight = self.getPageHeight()

        waits = 0
        retries = 0

        # Scroll down to trigger loading of new images
        if self.lastHeight == self.getPageHeight():
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
        else:
            return True

        # Wait till new images are loaded
        while currentHeight == self.getPageHeight():
            if waits > 30:
                waits = 0
                retries += 1
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight*0.8);"
                )
                if currentHeight == self.getPageHeight():
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
            if retries > 5:
                print("Page has less than requested images")
                return False
            waits += 1
            sleep(0.2)
        sleep(0.2)

        return True

    def load_fetch_posts(self):
        """Load and fetch target account posts"""

        try:
            self.extractImages()

            # 12 posts loads up when we open the profile
            if self.no_of_posts > 12:
                # Loading all the posts
                print("Loading all the posts...")
                # Every time the page scrolls down we need to get the source code as it is dynamic
                while len(self.image_list) < self.no_of_posts:
                    hasMore = self.loadMore()
                    if not hasMore:
                        break
                    self.lastHeight = self.getPageHeight()
                    # Scroll to the bottom to get images into DOM
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    self.extractImages()
                    sleep(0.5)

        except Exception as e:
            print(
                "Some error occurred while scrolling down and trying to load all posts.",
                e,
            )
            sys.exit()

    def download_posts(self):
        """ To download all the posts of the target account """
        self.load_fetch_posts()
        no_of_images = len(self.image_list)
        if no_of_images > self.no_of_posts:
            self.image_list = self.image_list[: self.no_of_posts]
            no_of_images = self.no_of_posts

        for index, img in enumerate(self.image_list, start=1):
            try:
                filename = self.target_username + "_" + str(index) + ".jpg"
                image_path = os.path.join(self.imagesData_path, filename)
                link = img.get("src")
                response = requests.get(link, stream=True)

                print("Downloading image {0} of {1}".format(index, no_of_images))
                with open(image_path, "wb") as file:
                    shutil.copyfileobj(response.raw, file)
            except Exception as e:
                print(e)
                print("Couldn't download image {0}.".format(index))
                print("Link for image {0} ---> {1}".format(index, link))
        print("Download completed!")


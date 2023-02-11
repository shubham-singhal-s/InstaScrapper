"""
Hey Everyone!
This program can be used to scrape photos from any Instagram account
(if the logged in user follows that account or it's an open account).
"""
__author__ = "Darshan Majithiya, Shubham Singhal"
__email__ = "darsh2115@gmail.com, shubham21197@gmail.com"

import time
import traceback
from time import sleep
import sys
import os
# import shutil
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


class Scraper:
    def init_browser(self, options):
        try:
            # Web driver for selenium. Varies per OS and browser.
            driver = webdriver.Chrome(
                "IGScrapper/chromedriver_windows32/chromedriver.exe", chrome_options=options
            )
            self.main_url = "https://www.instagram.com"
        except Exception as e:
            print("Error initialising Selenium", e)
        # check the internet connection and if the home page is fully loaded or not.
        try:
            driver.get(self.main_url)

        except TimeoutError:
            print(
                "Loading took too much time. Please check your connection and try again."
            )
            sys.exit()
        return driver

    def __init__(self, username, password, target_username, nOfPosts, pType):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.type = pType
        self.image_list = []

        prefix = ""
        if self.type == "hash":
            prefix = "#"

        # Get image directories
        self.base_path = os.path.join("IGScrapper", "data", prefix + self.target_username)
        self.images_data_path = self.base_path
        self.no_of_posts = nOfPosts
        print(self.target_username, self.no_of_posts)
        options = Options()

        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        self.driver = self.init_browser(options)

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "loginForm"))
            )
        except Exception as e:
            print(e)

        # Login and go to requested page
        self.login()
        self.open_target_profile()

        # Check if the directory to store data exists
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

        # Start downlaod
        self.download_posts()

    def login(self):
        # Fill in user details
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
            time.sleep(0.5)
            login_link = self.driver.find_element_by_xpath('//div[text()="Log in"]')
            login_link.click()
        except Exception:
            print("Unable to find the Login button.")
            sys.exit()

        print("Logging in...")

        # Wait for user to log in else throw error
        # try:
        #     WebDriverWait(self.driver, 30).until(
        #         EC.presence_of_element_located((By.XPATH, '//span[text()="Search"]'))
        #     )
        # except Exception as e:
        #     print(
        #         "Please try again with correct credentials or check your connection.", e
        #     )
        #     sys.exit()
        sleep(10)

        print("Login Successful!")

    def open_target_profile(self):
        target_profile_url = ""
        if self.type == "acc":
            target_profile_url = self.main_url + "/" + self.target_username
        elif self.type == "search":
            target_profile_url = self.main_url + "/explore/search/keyword/?q=" + self.target_username.replace(" ", "%20")
        else:
            target_profile_url = self.main_url + "/explore/tags/" + self.target_username
        print("Redirecting to {} {}...".format(self.target_username, self.type))

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

    def extract_images(self):
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        all_images = soup.find_all("img", attrs={"style": "object-fit: cover;"})
        for img in all_images:
            if img not in self.image_list:
                self.image_list.append(img)
        print("Loaded {} images.".format(len(self.image_list)))

    def get_page_height(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    def load_fetch_posts(self):
        """Load and fetch target account posts"""

        try:
            self.extract_images()

            # 12 posts loads up when we open the profile
            if self.no_of_posts > 12:
                # Loading all the posts
                print("Loading all the posts...")
                # Every time the page scrolls down we need to get the source code as it is dynamic
                total_tries = 0
                while len(self.image_list) < self.no_of_posts:
                    if total_tries > 30:
                        print("Page contains less images than requested.")
                        return
                    self.extract_images()

                    current_height = self.get_page_height()
                    retries = 0

                    # Scroll down to load more content
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    sleep(1)
                    self.extract_images()

                    self.driver.execute_script("window.scrollTo(0, 0);")

                    failed = False
                    # Wait till new content loads or quit after 20 seconds of waiting
                    while current_height == self.get_page_height():
                        if retries > 8:
                            total_tries += 1
                            failed = True
                            print("Skipping this loop")
                            break
                        retries += 1
                        sleep(0.2)
                    if failed:
                        continue
                    # Scroll to the bottom to get images into DOM
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    total_tries = 0
                    sleep(0.5)
                    self.extract_images()

        except Exception as e:
            print(
                "Some error occurred while scrolling down and trying to load all posts.",
                e,
            )
            sys.exit()

    def download_posts(self):
        """ To download all the posts of the target account """
        self.load_fetch_posts()
        sleep(5)
        self.driver.quit()
        no_of_images = len(self.image_list)
        if no_of_images > self.no_of_posts:
            self.image_list = self.image_list[: self.no_of_posts]
            no_of_images = self.no_of_posts
        print("Downloading {} images".format(no_of_images))

        cpus = cpu_count()
        results = ThreadPool(cpus - 1).imap_unordered(self.download_url, enumerate(self.image_list, start=1))

        for result in results:
            print('Downloading {} of {}'.format(result[1], no_of_images))
        # for index, img in enumerate(self.image_list, start=1):
        #     try:
        #         filename = self.target_username + "_" + str(index) + ".jpg"
        #         image_path = os.path.join(self.images_data_path, filename)
        #         link = img.get("src")
        #         response = requests.get(link, stream=True)

        #         print("Downloading image {0} of {1}".format(index, no_of_images))
        #         with open(image_path, "wb") as file:
        #             shutil.copyfileobj(response.raw, file)
        #     except Exception as e:
        #         print(e)
        #         print("Couldn't download image {0}.".format(index))
        #         print("Link for image {0} ---> {1}".format(index, link))
        print("Download completed!")

    def download_url(self, args):
        fn, img = args[0], args[1]
        try:
            filename = self.target_username + "_" + str(fn) + ".jpg"
            image_path = os.path.join(self.images_data_path, filename)
            url = img.get("src")
            r = requests.get(url)
            with open(image_path, 'wb') as f:
                f.write(r.content)
            return(url, fn)
        except Exception as e:
            print('Exception in download_url():', e)

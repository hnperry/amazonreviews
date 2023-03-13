# Create Environment

import requests
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime
from urllib.parse import urlencode

# Create User-Agent

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

# Sent get request to url

URL = 'https://www.amazon.com/Wind-Up-Bird-Chronicle-Vintage-International-ebook/product-reviews/B003XT605Y/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
webpage = requests.get(URL, headers = HEADERS)

# Create soup

soup = bs(webpage.content, "lxml")

# Obtain title with regex magic

title = soup.find("div", attrs = {"class" : 'a-row product-title'})
title_string = title.string.strip()
clean_title = re.findall('^(.+?):', title_string)
clean_title = clean_title[0]
clean_title.rstrip()
print("Scraping Reviews from", clean_title)

# Pass API key so Jeff Bezos doesn't get angry with me
# API key has been changed to protect my wallet

params = {'api_key': "547e3e994ea35cf8187aswf2314cd6s772", 'url': URL}
response = requests.get('http://api.scraperapi.com/',   params=urlencode(params))
reviewsoup = bs(response.text, 'html.parser')

# Set up lists for raw data

reviewers = []
review_dates = []
ratings = []

# Set up lists for clean data

reviewers_clean = []
review_dates_clean = []
ratings_clean = []
review_text_clean = []

# Scrape first page

print("Scraping page 1...")

# Obtain reviewer names

data_string = ""

for item in reviewsoup.find_all("span", class_="a-profile-name"):
    data_string = data_string + item.get_text()
    reviewers.append(data_string)
    data_string = ""

# Since an Amazon review page will showcase the top positive and critical reviews at the top of each page, we need to remove them from our dataset each time

reviewers_clean = reviewers_clean + reviewers[2:]
reviewers = []

# Obtain review dates
# Dates come in the form "December 20, 2022" so we need to parse them with regex and use datetime to convert them to the format we want

for item in reviewsoup.find_all("span", class_="a-size-base a-color-secondary review-date"):
    data_string = data_string + item.get_text()
    clean_date = re.findall('on (.+)', data_string)
    datestring = clean_date[0]
    date = datetime.strptime(datestring,'%B %d, %Y').date()
    date = str(date)
    review_dates.append(date)
    data_string = ""

# The top positive and critical reviews also include date data, so we need to remove those from this dataset as well

review_dates_clean = review_dates_clean + review_dates[2:]
review_dates = []

# Obtain ratings
# Ratings come in the format "4.0 out of 5.0 stars" so we only need to grab the first three characters here

for item in reviewsoup.find_all("span", class_="a-icon-alt"):
    data_string = data_string + item.get_text()
    data_string = data_string[:3]
    ratings.append(data_string)
    data_string = ""

# On each page of reviews there is the average overall rating, and the ratings from the top positive and critical reviews
# So we will remove the first three ratings from each page before adding them to our dataset

ratings_clean = ratings_clean + ratings[3:]
ratings = []

# I found that the review text came correct every time, so I did not clean the reviews here

for item in reviewsoup.find_all("span", class_="a-size-base review-text review-text-content"):
    data_string = data_string + item.get_text()
    data_string = data_string.strip()
    review_text_clean.append(data_string)
    data_string = ""

# Scrape subsequent pages using the same method

# Provide base URL which we will use to cycle through each page by appending the page number to the end of the URL

BASEURL = 'https://www.amazon.com/Wind-Up-Bird-Chronicle-Vintage-International-ebook/product-reviews/B003XT605Y/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber='

page = 2

# Use while loop to loop through each page, grabbing the data from each page

while page < 130:
    
    #Change URL to loop through pages

    URL = BASEURL + str(page)

    print("Scraping page", page)
        
    params = {'api_key': "547e3e238eweq573h81314cbe5095a32", 'url': URL}
    response = requests.get('http://api.scraperapi.com/',   params=urlencode(params))
    reviewsoup = bs(response.text, 'html.parser')

    # Extract review dates     

    for item in reviewsoup.find_all("span", class_="a-size-base a-color-secondary review-date"):

        data_string = data_string + item.get_text()
        clean_date = re.findall('on (.+)', data_string)
        datestring = clean_date[0]
        date = datetime.strptime(datestring,'%B %d, %Y').date()
        date = str(date)
        review_dates.append(date)
        data_string = ""

    # At this point I encountered an issue where some pages would display an ad that used the same span class tag, so the data would get messed up
    # I decided to add in a function to skip any page that does not contain exactly the amount of review dates we expect
    # Because in the wise words of Sweet Brown, ain't nobody got time for that

    if len(review_dates) != 12:
        print("Skipped page", page)
        review_dates = []
        page = page + 1
        continue
    
    #Extract reviewer names

    for item in reviewsoup.find_all("span", class_="a-profile-name"):
       
        data_string = data_string + item.get_text()
        reviewers.append(data_string)
        data_string = ""

    # The ad situation also created problems on some of the reviewer data, so we skipped any pages with ads here as well

    if len(reviewers) != 12:
        print("Skipped page", page)
        review_dates = []
        reviewers = []
        page = page + 1
        continue

    # Extract review ratings

    for item in reviewsoup.find_all("span", class_="a-icon-alt"):
        data_string = data_string + item.get_text()
        data_string = data_string[:3]
        ratings.append(data_string)
        data_string = ""
    
    # Same story- skip the page if we don't get the expected amount of ratings

    if len(ratings) != 13:
        print("Skipped page", page)
        review_dates = []
        reviewers = []
        ratings = []
        page = page + 1
        continue

    # Collect review text- luckily this was clean every time so no need to manipulate it or skip pages

    for item in reviewsoup.find_all("span", class_="a-size-base review-text review-text-content"):
        data_string = data_string + item.get_text()
        data_string = data_string.strip()
        review_text_clean.append(data_string)
        data_string = ""

    # All in all, we only skipped around 5-10 pages per book which is a drop in the bucket for many of these
    # If we got this far, add data to clean lists and dump lists for reuse
    
    review_dates_clean = review_dates_clean + review_dates[2:]
    reviewers_clean = reviewers_clean + reviewers[2:]
    ratings_clean = ratings_clean + ratings[3:]

    review_dates = []
    reviewers = []
    ratings = []

    # Advance to next page
    
    page = page + 1


#After the process is done, print statements to verify that we have extracted the exact same amount of data for each point

print("Found", len(reviewers_clean), "reviewers")
print("Found", len(review_dates_clean), "review dates")
print("Found", len(ratings_clean), "ratings")
print("Found", len(review_text_clean), "review texts")

# Now I will make a unique ID for each review

unique_id = []
inc=1

for i in ratings_clean:
    unique_id.append(inc)
    inc = inc + 1

print("Created", len(unique_id), "unique IDs.")

# Put the data into a database

# For reference, I set up the database as follows:

# CREATE TABLE Reviews (
# id INTEGER PRIMARY KEY NOT NULL UNIQUE,
# name TEXT NOT NULL,
# date DATE NOT NULL,
# rating FLOAT NOT NULL,
# review_text TEXT,
# book INTEGER);

# CREATE TABLE Books (
# id INTEGER,
# name TEXT );

# Now we are going to put the data into the database

import sqlite3

# Connect to sqlite and create cursor object

conn = sqlite3.connect('murakamiamazondata.db')
cur = conn.cursor()

# Insert data into Reviews table

for a,b,c,d,e in zip (unique_id, reviewers_clean, review_dates_clean, ratings_clean, review_text_clean):
    cur.execute(
        "INSERT INTO Reviews (id, name, date, rating, review_text, book) values (?, ?, ?, ?, ?, ?)",
        (a, b, c, d, e, 1)
    )

# Insert data into Books table
# I cycled through numbers 1 - 10 as the book id for each book

cur.execute(
    "INSERT INTO Books (id, name) values (?, ?)",
    (1, clean_title)
    )

# Commit changes and close connection

conn.commit()
conn.close()

print("Data successfully inserted")

# I ran this code for each book changing the URLs, unique id start number, number of pages the while loop would cycle through, and the book id number
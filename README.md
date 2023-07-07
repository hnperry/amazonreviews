# Evaluating Customer Sentiment: Web Scraping and Visualizing Amazon Reviews

The idea for this project came to me during book club- we were reading one of Haruki Murakami’s novels, and the opinions seemed mixed. If you aren’t familiar with Murakami, he is a critically-acclaimed Japanese author best known for his magical realism-style novels. From his metaphorically rich dream-like sequences to his taboo and graphic depictions of sex and gore, Murakami’s novels can be quite polarizing in the literature world. After seeing the reactions of the members of the book club I became curious about what the general population thinks of his books, so I turned to the modern-day Agora: Amazon reviews.

The dataset and code are available in this repository. Please [click here](https://public.tableau.com/views/AmazonBookReviewsHarukiMurakami/Dashboard1?:language=en-US&:display_count=n&:origin=viz_share_link) to view the below visualization on Tableau. Note: Please view the viz in *desktop mode*.

<div class='tableauPlaceholder' id='viz1678737071451' style='position: relative'><noscript><a href='#'><img alt='Dashboard 1 ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Am&#47;AmazonBookReviewsHarukiMurakami&#47;Dashboard1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='AmazonBookReviewsHarukiMurakami&#47;Dashboard1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Am&#47;AmazonBookReviewsHarukiMurakami&#47;Dashboard1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>    

<br>

## Step 1: Data collection

First, let's import the relevant libraries

```
import requests #for sending HTTP requests
from bs4 import BeautifulSoup as bs #for pulling data from HTML and XML files
import re #to alter string data
from datetime import datetime #for working with date data
from urllib.parse import urlencode #to encode query strings in URLs
```

I decided which books to include in this project by sorting all of Murakami’s novels from most to least reviewed on Amazon, and selecting the top 10 from that list. This will allow me to get a large sample size that minimizes outlier influence as much as possible. The process I am about to describe was repeated ten times, once for each book.
I scrolled through the reviews and pinpointed the data I was most interested in. This included the reviewer names, review dates, star ratings (1–5), review texts, and book names.
To start, I created a user agent, sent a request to the URL of our reviews page, and used Beautifulsoup to parse the XML.

```
# Create User Agent and send request
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
URL = 'https://www.amazon.com/Wind-Up-Bird-Chronicle-Vintage-International-ebook/product-reviews/B003XT605Y'
webpage = requests.get(URL, headers = HEADERS)

# Parse XML
soup = bs(webpage.content, "lxml")
```

I gathered my data by examining the HTML structure of the webpage and identifying the CSS selector of each data point I wanted. The title is in the div tag, under the “class” attribute. The title of the first book is listed as “The Wind-Up Bird Chronicle: A Novel (Vintage International),” so I used regex magic to split the title around the “:” and grab the relevant portion.
  
```
title = soup.find("div", attrs = {"class" : 'a-row product-title'})
title_string = title.string.strip()
clean_title = re.findall('^(.+?):', title_string)
clean_title = clean_title[0]
clean_title.rstrip()
```
Next, I set up lists to store the data. These lists correspond to the data points mentioned previously: reviewer names, review dates, ratings, and review texts. The raw data lists were used to scrape data from each page, and the clean lists were used to keep a running list of the data scraped so far. You may notice that there is no raw list for the review text- that is because it came out as expected every time and there was no need to manipulate it.

```
# Lists for storing raw data
reviewers = []
review_dates = []
ratings = []

# Lists for storing clean data
reviewers_clean = []
review_dates_clean = []
ratings_clean = []
review_text_clean = []
```
Next, I proceeded with scraping the web pages. Since I already established a connection to the first page to scrape the title, I grabbed the reviewer names, review dates, ratings, and review text data from the first page. I did this by locating the CSS selector for each of these data points and looping through the HTML of each page to grab them all. My approach scraping subsequent pages was as follows:
 
```
# Provide base URL which we will use to cycle through each page 

BASEURL = 'https://www.amazon.com/Wind-Up-Bird-Chronicle-Vintage-International-ebook/product-reviews/B003XT605Y/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber='

page = 2

# Use while loop to loop through each page, grabbing the data from each page
# In this case, there were 129 pages of reviews

while page < 130:
    
    #Change URL to loop through pages
    URL = BASEURL + str(page)
    print("Scraping page", page)
    
    #Note: API Key has been changed for security reasons
    params = {'api_key': "547e3e99dfdsa3343378781314dhe5095a32", 'url': URL}
    response = requests.get('http://api.scraperapi.com/',   params=urlencode(params))
    reviewsoup = bs(response.text, 'html.parser')

    # Extract and re-format review dates
    # The review dates were originally strings formatted like "Reviewed on December 20, 2021"
    # So I used regex to get the portion after the word "on "
    # And then I used datetime to put the date string in a format we like, "12-20-2011"

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

    # Extract and re-format review ratings
    # These orignially were strings formatted as "4.0 out of 5.0 stars"
    # So we grabbed the first 3 characters of the string

    for item in reviewsoup.find_all("span", class_="a-icon-alt"):
        data_string = data_string + item.get_text()
        data_string = data_string[:3]
        ratings.append(data_string)
        data_string = ""
    
    # Same story- skip the page if we dont get the expected amount of ratings
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

    # All in all, we only had to skip around 5-10 pages per book 
```
After this, I had the reviewer name, review date, rating, and review text data stored in lists. The raw data from the first three lists looked like this:

reviewers = [‘Gabby M’, ‘blewis’, ‘blewis’, ‘Sinuous’, ‘fra7299’, ‘Rich’, ‘nunh’, ‘Zephyr’, ‘Rea’, ‘V. Laluz’, ‘Mark G.’, ‘Kindle Customer’]

review_dates = [‘2022–12–30’, ‘2022–11–17’, ‘2022–11–17’, ‘2012–02–17’, ‘2013–12–14’, ‘2012–04–15’, ‘2012–10–24’, ‘2014–07–29’, ‘2013–07–09’, ‘2009–06–03’, ‘2022–09–20’, ‘2022–07–15’]

ratings = [4.5, 4.0, 3.0, 3.0, 4.0, 5.0, 5.0, 5.0, 4.0, 5.0, 5.0, 5.0, 4.0]

I noticed that the scraper was picking up 12 reviewers, 12 review dates, and 13 ratings per page. This is due to the structure of the webpage- each Amazon review page displays the overall rating, and then the top positive and top critical reviews. Gabby M and blewis provided these reviews, so their data needs to be removed from the list each time if we want the review data to match up. We also need to remove the first three ratings of each page to account for the overall rating, Gabby M’s rating, and blewis’ rating.

So, my process for each page went like this:

Loop through all the data points and store the data in the raw list
Check whether the length of the list matches the expected length
If at any point the length of the list does not match what is expected, skip the page
If all the lists match their expected length at the end of the page, store the relevant data in the clean list, dump the raw data list for re-use, and advance to the next page
                 
```
# This is still in the while loop
   
    # Add relevant data to clean lists
    # Removing the first 2, 2, and 3 items from the review dates, reviewers, and ratings list, respectively
    review_dates_clean = review_dates_clean + review_dates[2:]
    reviewers_clean = reviewers_clean + reviewers[2:]
    ratings_clean = ratings_clean + ratings[3:]

    # Empty raw data lists for reuse
    review_dates = []
    reviewers = []
    ratings = []

    # Advance to next page
    page = page + 1
```
                 
Repeating this process for each page gave us 1160 records for the first book. Next, I created a unique id for each record in preparation for inserting it into the database.
                 
```
unique_id = []
inc=1

for i in ratings_clean:
    unique_id.append(inc)
    inc = inc + 1
```

Since I had to use an API with a limited number of free credits and I wanted my data in two tables, I decided to move my data into a local database called SQLite. The Reviews table will contain the unique id, reviewer name, review date, rating, review text, and book id. The Books table will contain the book id and name of each book. I set up my database with the following query:
                 
```
CREATE TABLE Reviews (
  id INTEGER PRIMARY KEY NOT NULL UNIQUE,
  name TEXT NOT NULL,
  date DATE NOT NULL,
  rating FLOAT NOT NULL,
  review_text TEXT,
  book INTEGER);

CREATE TABLE Books (
  id INTEGER,
  name TEXT );
```
                 
Next, I connected to the database and created a cursor object so I could interact with the database from within Python. I inserted the data by looping through the lists of clean data and executing SQL code via the cursor object.
                 
```
# Create cursor object
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
```
                 
I repeated this process for each of the 10 books by changing the base URL, unique id starting number, number of pages to scrape, and book id number as needed. At the end of the process, we had a total of 7900 records in the Reviews table, and 10 records in the Books table. Yay!

Next, I wanted to combine my data from the two tables to create one all-encompassing dataset. I queried the database with the following SQL code:
                 
```
SELECT 
 Reviews.id as review_id, 
 Reviews.name as reviewer_name, 
 Reviews.date as review_date, 
 Reviews.rating as review_rating, 
 Reviews.review_text, 
 Books.name as book_name
FROM 
 Reviews
JOIN 
 Books 
ON 
 Books.id = Reviews.book
```
                 
## Step 2: Data Cleaning

After querying our database and exporting our results to Excel, I ended up with 7900 records of data. My steps for cleaning the data are below:

1. Removed duplicate and blank records
2. Since this is Amazon, there may be people who are reviewing the quality of service they received from Amazon rather than the book. I searched for the keywords “damaged,” “broken,” “delivered,” “arrived,” “book cover,” “book jacket,” “disappointed,” “condition,” “shipping,” “ripped,” “torn,” “unhappy,” “unsatisfied,” “bad,” “product,” “quality,” “counterfeit,” “cheap,” “broke,” “wrong,” “useless,” “crap,” “junk,” “worst,” “error,” “shame,” “garbage,” “hated,” “bother,” “annoy,” “condition,” “arrived,” and “amazon,” and removed reviews that were not assessing the quality of the novel. I came to these words by referencing [this sentiment analysis paper by RIT scholar Ammar Rashed Hamdallah](https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=12196&context=theses) which identified the most frequently used words in Amazon reviews.
3. I found a few instances of reviews along the lines of “5 stars for Murakami, 0 for the publisher’s quality”, so I updated those to reflect their opinion of the actual book.
4. I deleted reviews not in English, which will be important for future textual analysis. I translated a few simple reviews saying “Excelente,” “Tres bien,” etc. to preserve as much data as possible.
5. Removed all non-English characters that were distorted during data transfer, i.e. “Ä”, “ü,” etc. I also removed all extra spaces in the review text.
At the end of the data cleaning process, we end up with 7709 records of English reviews of the top 10 most reviewed Murakami novels on Amazon.

## Step 3: Data analysis and visualization

For some initial EDA, I ran summary statistics for the ratings data in Excel
                 
```
review_rating 
 
Mean 4.093527046
Standard Error 0.013579607
Median 5
Mode 5
Standard Deviation 1.192301841
Sample Variance 1.421583679
Kurtosis 0.503873346
Skewness -1.231710997
Range 4
Minimum 1
Maximum 5
Sum 31557
Count 7709
```
                 
These summary statistics give us some insight into our data. First of all, things are looking good for Murakami with a median star rating of 5. This means at least 50% of the ratings are 5-star ratings. The standard deviation tells us the typical distance the values in the distribution are from the mean. With a mean of 4.09 and a standard deviation of 1.19, we know that most of the ratings are between 3 and 5 stars. A skew value of -1.23 corroborates this, showing us that the data is skewed left. The standard error tells us how accurate the mean of any given sample is likely to be compared to the true population mean. From the small standard error of 0.0135, we can infer that although we had to skip pages in our data collection, our sample size is an accurate representation of the whole population. This summary data gives us a roadmap as to what kind of data visualization would be interesting here.

At this point I think the [Tableau visualization](https://public.tableau.com/app/profile/nikki.perry/viz/AmazonBookReviewsHarukiMurakami/Dashboard1) speaks for itself, but I will include some screenshots here to provide narrative context. As I said before, please view the Tableau page in desktop mode.
                 
![Average Rating by Book Title](https://user-images.githubusercontent.com/116209783/232593278-93cda7a1-4b81-4083-9ad8-ef7e98af4a53.png)
                 
The “Average Rating by Book Title” graph shows us the average rating of each book compared to all of the books. The average ratings range from 4.3954 to 3.8194 which shows that in general, Amazon customers rated his novels quite positively. With an average rating of 4.3954, the highest-rated book is Hard-Boiled Wonderland and the End of the World. So there’s a book recommendation- on the house!
                 
![Ratings Over Time](https://user-images.githubusercontent.com/116209783/232593459-127afcc1-c3fb-4118-bf42-a360576bf9f5.png)

Our “Ratings Over Time” graph compares the ratings of each book over time. The size of the bubbles correlates to the number of reviews given during that year, with larger bubbles indicating more reviews. The trend line shows whether the book ratings have trended positively or negatively over time. From this visualization, we learn that the ratings for After Dark have had the largest positive change with a trend line slope of 0.03533, while the largest negative change in ratings was for Colorless Tsukuru Tazaki and His Years of Pilgrimage with a slope of -0.078266. The ratings for Sputnik Sweetheart have stayed the most consistent, with the trend line sloping at only -0.00452. Here we can also observe the number of reviews given to each book and see that 1Q84 received the most reviews while Sputnik Sweetheart received the least.
                 
![Distribution of Ratings](https://user-images.githubusercontent.com/116209783/232593611-8afacc76-9b9a-4dbb-8016-1f625671aa66.png)
                 
The “Distribution of Ratings” graph shows how the ratings were distributed across the 1–5 star rating option. This graph visually demonstrates our negative skew, where most of our data is on the right. Out of 7709 total ratings, 52% were five-star ratings while only 5.8% were one-star ratings. This also raises an interesting question- are readers more likely to leave reviews for a book they had a positive experience with?
                 
![Perception Over Time](https://user-images.githubusercontent.com/116209783/232593705-a02d9938-997d-47d3-bbe2-e396bf2fba6d.png)
                 
The perception over time graph shows the average ratings of all the books over time. Unfortunately for Murakami, it looks like his ratings have been trending ever so slightly negatively with the trend line having a slope of -0.00005. Despite this, the average rating for any quarter of any year has never dipped below 3.371, its rating in Q4 of 2011
                 
![Biggest Murakami Fans](https://user-images.githubusercontent.com/116209783/232593804-b7fb12db-d0a1-4353-a8f2-23cb0c5ec412.png)
                 
The “Biggest Murakami Fans” graph was made after I noticed that Amazon customer lindaluane had left a whopping 11 reviews across 10 books! Not only has she reviewed every book on the list, but she also came back to re-review one of the books after a second read. I put this together as a fun little appreciation for the customers who provided the data for this project.

That’s the end of the data story for now. Areas for future study include textual analysis of the review text data, such as sentiment analysis, topic modeling, or term frequency studies.

If you made it this far, thank you for reading!



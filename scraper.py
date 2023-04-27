import requests
from bs4 import BeautifulSoup
from pprint import pprint
import time
import sqlite3
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Download required NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')


HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
           'Accept-Language': 'en-US, en;q=0.5'})
url = 'https://www.amazon.in/Apple-New-iPhone-12-128GB/dp/B08L5TNJHG/'

# will hold all the reviews in a dictionary format
reviewsList = []


# url: takes the url of the page and returns the soup

def getSoup(url):
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, 'html.parser')

    return soup

# this returns the link to the 'all reviews page'


def getAllReviewsPage(soup):
    allReviews = soup.find(
        'a', {'data-hook': 'see-all-reviews-link-foot'})['href']
    return allReviews

# returnes the reviews extracted from the soup


def getReviews(soup):
    # Getting the reviews
    reviews = soup.find_all('div', {'data-hook': 'review'})
    # product info
    productInfo = soup.find(
        'a', {'data-hook': 'product-link'}).text.strip().split('- (Product) ')
    #  Framing processedReview as dictionary
    # this the product info: model, colour, storage
    # Getting Review Title, Review Text, Verified Pruchase
    for item in reviews:
        processedReview = {}
        processedReview['Storage'] = productInfo[0].strip()
        processedReview['Color'] = productInfo[1].strip()
        processedReview['Title'] = item.find(
            'a', {'data-hook': 'review-title'}).text.strip()
        processedReview['Body'] = item.find(
            'span', {'data-hook': 'review-body'}).span.text.strip()
        processedReview['Rating'] = item.find(
            'i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()
        verifiedPurchase = item.find(
            'span', {'data-hook': 'avp-badge'}).text.strip()

        if verifiedPurchase is not None:
            processedReview['verifiedPurchase'] = 'Yes'
        else:
            processedReview['verifiedPurchase'] = 'No'

        reviewsList.append(processedReview)
    return reviewsList

# this deletes the table name passed to it


def deleteData(table):
    # Connect to the database
    conn = sqlite3.connect('Reviews.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Fetch all the table names using a query
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # table_names = [row[0] for row in cursor.fetchall()]

    # # Print the table names
    # print(table_names)

    # Execute the DROP TABLE query
    cursor.execute(f"DROP TABLE IF EXISTS {table};")

    # Commit the changes
    conn.commit()
    # Close the connection
    conn.close()

# stored the reviews into the sqlite3 db


def storeData(reviews):
    # Connect to the SQLite database
    conn = sqlite3.connect('Reviews.db')

    # Create a new table called "reviews"
    conn.execute('''CREATE TABLE IF NOT EXISTS reviews
                (id INTEGER PRIMARY KEY,
                title TEXT,
                body TEXT,
                storage TEXT,
                color TEXT,
                verified_purchase TEXT,
                rating TEXT)''')

    # Insert the dictionary data into the "reviews" table
    conn.executemany('INSERT INTO reviews (title, body, storage, color, verified_purchase, rating) VALUES (?, ?, ?, ?, ?, ?)',
                     [(r['Title'].lower(), r['Body'].lower(), r['Storage'].lower(), r['Color'].lower(), r['verifiedPurchase'].lower(), r['Rating'].lower()) for r in reviews])

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# fetches all the data stored in the db


def checkData():
    # Connect to the SQLite database
    conn = sqlite3.connect('Reviews.db')

    # Retrieve all rows from the "reviews" table
    cursor = conn.execute('SELECT * FROM reviews')
    rows = cursor.fetchall()

    # Print the rows
    for row in rows:
        print(row, end='\n')

    # Close the connection
    conn.close()

# best, worst keywords


def bestWorstKeywords(processedReview):
    text = processedReview['Title'] + " " + processedReview['Body']

    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)

    words = word_tokenize(text)

    # Remove stop words (like "the", "and", "a") from the text
    stop_words = set(stopwords.words('english'))

    filtered_words = [word for word in words if word.casefold()
                      not in stop_words]

    # Perform sentiment analysis on each sentence
    sia = SentimentIntensityAnalyzer()

    sentiment_scores = [sia.polarity_scores(
        sentence)['compound'] for sentence in sentences]

    # Combine the filtered words with their corresponding sentiment scores
    word_scores = list(zip(filtered_words, sentiment_scores))

    # Sort the words by their sentiment score, from highest to lowest
    word_scores_sorted = sorted(word_scores, key=lambda x: x[1], reverse=True)

    # Extract the best and worst keyword
    best_keyword = word_scores_sorted[0][0]

    worst_keyword = word_scores_sorted[-1][0]

    print(f"Best word = {best_keyword}")

    print(f"worst word = {worst_keyword}\n")


# ==============================================================driver============================================
# main code to run all the operations
def driver():
    # current page data
    soup = getSoup(url)
    # link to the all reviews page
    allRevLink = 'https://www.amazon.in'+getAllReviewsPage(soup)

    # TODO: work for multiple pages
    # for i in range(10):
    #     # new link
    #     nextpage = allRevLink+'&pageNumber='+str(i)
    #     # make soup of the current page
    #     currentSoup = getSoup(nextpage)
    #     # get all the reviews of the current soup/page
    #     currentReviews = getReviews(currentSoup)
    # -----------------------working---------------------------

    # ------------------getting reviews for current page
    reviews = getReviews(getSoup(allRevLink))
    bestWorstKeywords(reviews[1])
    # deleteData('reviews')
    # storeData(reviews)
    # checkData()


# ========================================driver code===============================
driver()

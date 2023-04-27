import sqlite3
import spacy
from textblob import TextBlob
from pprint import pprint
from flask import Flask, request, jsonify, render_template

# sentiment analysis using spacy (en_core_web_sm)
# def spacyAnalysis(rows):
#     # Load the pre-trained spaCy English model for sentiment analysis
#     nlp = spacy.load('en_core_web_sm')
#     # Loop through the rows and perform sentiment analysis on the "Body" column of each row
#     for row in rows:
#         doc = nlp(row[2])
#         print('Review Text:', row[2])
#         print('Sentiment:', doc.sentiment)

# sentiment analysis using textblob
# def textBlobAnalysis(rows):
#     # Loop through the rows and perform sentiment analysis on the "Body" column of each row
#     for row in rows:
#         blob = TextBlob(row[2])
#         report = {
#             'Text': row[2],
#             'polarity': blob.sentiment.polarity,
#             'subjectivity': blob.sentiment.subjectivity,
#         }
#         pprint(report)

def spacyAnalysis(review):
    # Load the pre-trained spaCy English model for sentiment analysis
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(review)
    report = {
        'Review Text': review,
        'Sentiment': doc.sentiment
    }
    print(report)
    return report

def blobAnalysis(review):
    blob = TextBlob(review)
    report = {
        'Text': review,
        'polarity': round(blob.sentiment.polarity, 2),
        'subjectivity': round(blob.sentiment.subjectivity, 2),
    }
    return report

# gets the data from the database
def fetchData(db):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    if conn:
        print("Connected to db\n-------------------")
        # Retrieve all rows from the "reviews" table
        cursor = conn.execute('SELECT * FROM reviews')
        rows = cursor.fetchall()
        conn.close()
        return rows
    else:
        print('Connection Failed')

# =======================driver code=========================
def driver():
    # fetching the data from databse
    data = fetchData('Reviews.db')
    # spacyAnalysis(data)
    # textBlobAnalysis(data)


app = Flask(__name__)

@app.route('/')
def home():
    return "<h2>Add Either '/spacy' or '/textblob'</h2> "

# endpoint for statemenet analysis using spacy

@app.route('/spacy', methods=['GET', 'POST'])
def spacyRoute():
    if request.method == 'POST':
        # get the text from the text area
        text = request.form.get('input_text')
        report = spacyAnalysis(text)
        # return jsonify({'Sentiment': result})
        return report
    return '''
    <form method="POST">
        <h2>Write a review</h2>
        <label for="text_input"></label>
        <textarea name="input_text" style="width: 1000px; height: 250px;"></textarea>
        <button type="submit">Submit</button>
    </form>
    '''

# endpoint for statemenet analysis using textblob
@app.route('/textblob', methods=['GET', 'POST'])
def blobRoute():
    if request.method == 'POST':
        # get the text from the text area
        text = request.form.get('input_text')
        report = blobAnalysis(text)
        # return jsonify({'Sentiment': result})
        return report
    return '''
    <form method="POST">
        <h2>Write a review</h2>
        <textarea name="input_text" style="width: 1000px; height: 250px;"></textarea>
        <button type="submit">Submit</button>
    </form>
    '''


@app.route('/reviews', methods=['GET', 'POST'])
def fetchREview():
    reviews = []
    if request.method == 'POST':
        color = request.form.get('color').lower()
        storage = request.form.get('storage').lower()
        rating = float(request.form.get('rating'))
        
        # establish a connection with db
        conn = sqlite3.connect('reviews.db')
        # write query to fetch the reviews
        query = "SELECT body FROM reviews WHERE color=? AND storage like%?% AND rating=?"
        # execute the query with the inputs revieved from the user
        results = conn.execute(query, (color, storage, rating))

        results = conn.execute(query)
        # fetch all the rows from the result
        rows = results.fetchall()
        conn.close()
        for row in rows:
            rev = {}
            rev['review'] = row
            reviews.append(rev)

        return jsonify(rows)
    return '''
    <form method="POST">
        <h2>Enter Review Details</h2>
        Color:
        <input type="text" name="color"><br><br>
        Storage:
        <input type="text" name="storage"><br><br>
        Rating:
        <input type="text" name="rating"><br><br>
        <button type="submit">Submit</button>
    </form>        
    '''

if __name__ == '__main__':
    app.run(debug=True)
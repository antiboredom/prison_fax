#GOOD JOB IT LOOKS LIKE YOUR RATINGS ARE GOING UP! :) --- OH NO - IT SEEMS THAT YOUR AVERAGE STAR RATING IS FALLING :'(

import csv, urllib, time, json, datetime
from phaxio import PhaxioApi
from bs4 import BeautifulSoup
import ap, numpy as np

with open('credentials.json') as cfile:
    credentials = json.load(cfile)

fax_api = PhaxioApi(credentials['key'], credentials['secret'])

def send_fax(number, reviews, testing=True):
    """Concatenates and faxes reviews"""

    reviews = ["RATING: {0}/5.0\n{1}".format(r['rating'], r['content'].encode('utf-8')) for r in reviews]
    content = "CONGRATULATIONS YOU HAVE"
    if len(reviews) > 1:
        content += " NEW REVIEWS"
    else:
        content += " A NEW REVIEW"
    content += "\n\n" + "\n\n".join(reviews)

    if testing:
        # send to our test number
        print content
        #r = fax_api.send(to=['2129981898'], string_data=content, string_data_type='text')
    else:
        r = fax_api.send(to=[number], string_data=content, string_data_type='text')

def load_reviews(name):
    """Load reviews from disk"""
    filename = 'reviews/' + name.replace(' ', '_') + '.json'
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except:
        return []

def save_reviews(name, reviews):
    """Save reviews to disk"""
    filename = 'reviews/' + name.replace(' ', '_') + '.json'
    try:
        with open(filename, 'w') as f:
            json.dump(reviews, f, indent=2)
    except:
        return False

def graph_ratings(reviews):
    """Returns a graph of star ratings over time"""
    reviews = sorted(reviews, key=lambda k: datetime.datetime.strptime(k['date'], '%Y-%m-%d'))
    #graph = [[datetime.datetime.strptime(r['date'], '%Y-%m-%d'), float(r['rating'])] for r in reviews]
    y = [float(r['rating']) for r in reviews]
    x = range(0, len(y))
    p = ap.AFigure(draw_axes=False, newline='\n', plot_labels=False, shape=(80, 8), ylim=[0.0, 5.0])
    graph = p.plot(x, y, marker='+')
    #print graph
    #print '-' * 80
    return graph

def get_page(url):
    """Retrieve yelp reviews from a url"""
    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)
    reviews = []

    for review in soup.select('.review-content'):
        rating = review.select('.rating-very-large meta')[0].get('content')
        content = review.select('.review_comment')[0].text.strip()
        date = review.select('.rating-qualifier meta')[0].get('content')
        reviews.append({'rating': rating, 'content': content, 'date': date})

    return reviews

def scrape_yelp(name, url, fax):
    """ Grabs prison reviews
    Then finds new reviews and sends out faxes
    """
    url += '?sort_by=date_desc'
    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)

    # get all urls for pagination
    links = [url] + [l.get('href') for l in soup.select('.pagination-links a.page-option')]

    reviews = []
    for link in links:
        time.sleep(1)
        reviews += get_page(link)

    # find new reviews
    old_reviews = load_reviews(name)
    new_reviews = [r for r in reviews if r not in old_reviews]
    save_reviews(name, reviews)

    # fax it out
    if len(new_reviews) > 0:
        send_fax(fax, new_reviews)


if __name__ == "__main__":
    """ Iterate through all prisons and fax new reviews to them"""
    with open('prisons.csv', 'rb') as prisonfile:
        data = csv.reader(prisonfile)
        for prison in data:
            name, fax, url = prison
            #reviews = load_reviews(name)
            #graph_ratings(reviews)
            scrape_yelp(name, url, fax)

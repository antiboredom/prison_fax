import csv, urllib, time, json
from phaxio import PhaxioApi
from bs4 import BeautifulSoup

with open('credentials.json') as cfile:
    credentials = json.load(cfile)

fax_api = PhaxioApi(credentials['key'], credentials['secret'])

def send_fax(number, reviews):
    reviews = ["RATING: {0}/5.0\n{1}".format(r['rating'], r['content'].encode('utf-8')) for r in reviews]
    content = "CONGRATULATIONS YOU HAVE"
    if len(reviews) > 1:
        content += " NEW REVIEWS"
    else:
        content += " A NEW REVIEW"
    content += "\n\n" + "\n\n".join(reviews)
    print content
    #r = fax_api.send(to=[number], string_data=content, string_data_type='text')

def load_reviews(name):
    filename = 'reviews/' + name.replace(' ', '_') + '.json'
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except:
        return []

def save_reviews(name, reviews):
    filename = 'reviews/' + name.replace(' ', '_') + '.json'
    try:
        with open(filename, 'w') as f:
            json.dump(reviews, f, indent=2)
    except:
        return False

def get_page(url):
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
    url += '?sort_by=date_desc'
    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)
    links = [url] + [l.get('href') for l in soup.select('.pagination-links a.page-option')]
    reviews = []
    for link in links:
        time.sleep(1)
        reviews += get_page(link)

    old_reviews = load_reviews(name)
    new_reviews = [r for r in reviews if r not in old_reviews]
    save_reviews(name, reviews)

    if len(new_reviews) > 0:
        send_fax(fax, new_reviews)

with open('prisons.csv', 'rb') as prisonfile:
    data = csv.reader(prisonfile)
    for prison in data:
        name, url, fax = prison
        scrape_yelp(name, url, fax)

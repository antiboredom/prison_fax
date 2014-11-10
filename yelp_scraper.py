from bs4 import BeautifulSoup
import urllib, time

def get_page(url):
    """Retrieve yelp reviews from a url"""
    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)
    reviews = []

    for review in soup.select('.review-content'):
        rating = review.select('.rating-very-large meta')[0].get('content')
        content = review.select('p')[0].text.strip()
        date = review.select('.rating-qualifier meta')[0].get('content')
        reviews.append({'rating': rating, 'content': content, 'date': date})

    return reviews

def scrape(url, sleep=1, sort='date_desc'):
    """Grabs reviews from a yelp page"""
    url += '?sort_by=' + sort
    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)

    # get all urls for pagination
    links = [url] + [l.get('href') for l in soup.select('.pagination-links a.page-option')]

    reviews = []
    for link in links:
        time.sleep(sleep)
        reviews += get_page(link)

    return reviews

if __name__ == "__main__":
    import sys, json
    print json.dumps(scrape(sys.argv[1]), indent=2)

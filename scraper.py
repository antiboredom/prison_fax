from bs4 import BeautifulSoup
import urllib, json, time, os.path

base_url = 'http://www.bop.gov'
start_url = base_url + '/locations/list.jsp'
data = urllib.urlopen(start_url).read()
soup = BeautifulSoup(data)
fields = [
    ('title', '#title_cont h2'),
    ('subtitle', '#title_cont p'),
    ('address', '.adr'),
    ('email', '#email'),
    ('phone', '#phone'),
    ('fax', '#fax'),
    ('pop_gender', '#pop_gender'),
    ('pop_count', '#pop_count'),
    ('inmate_address', '#send_address_inmate .address-item'),
    ('staff_address', '#send_address_staff .address-item')
]

links = [l.get('href') for l in soup.select('#OuterCol a')]

output = []

def prison_info(url):
    url = base_url + url

    print 'scraping ' + url

    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)

    try:
        code = url.split('/')[-1]
        if code == '':
            code = url.split('/')[-2]
        json_url = 'http://www.bop.gov/PublicInfo/execute/phyloc?todo=query&output=json&code=' + code
        if os.path.exists('json/' + code + '.json') is not True:
            urllib.urlretrieve(json_url, 'json/' + code + '.json')
    except:
        print 'no json file'

    info = {}
    for field in fields:
        try:
            info[field[0]] = soup.select(field[1])[0].text.strip()
        except:
            continue

    try:
        commissary_url = base_url + soup.select('#comm_list a')[0].get('href')
        commissary_filename = commissary_url.split('/')[-1]
        info['commissary_filename'] = commissary_filename
        if os.path.exists('pdfs/' + commissary_filename) is not True:
            urllib.urlretrieve(commissary_url, 'pdfs/' + commissary_filename)
    except:
        print 'no commissary'

    output.append(info)

def save_to_json():
    with open('prisons.json', 'w') as jsonfile:
        json.dump(output, jsonfile, indent=2)

for link in links:
    prison_info(link)
    time.sleep(.3)

save_to_json()

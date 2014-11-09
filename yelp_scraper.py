import json, pprint


# https://github.com/gfairchild/yelpapi
from yelpapi import YelpAPI
import json, glob

yelp_api = YelpAPI('Og3Jqb_gCff9zz5XTs7IAw', 'Oh4OlaexbARJK3FMEyal9z1hLZ4', 'NHn0u4AYSxT5AtvFqvaNeD8BtDdxwlMn', 'h1ZpA6oRADU58G0RH7jwWsBWFE4')

for f in glob.glob("json/*.json"):
    with open(f, 'r') as jfile:
        data = json.load(jfile)
        if 'Addresses' not in data.keys():
            continue
        address_info = next((item for item in data['Addresses'] if item['addressTypeName'] == "Physical Address"), None)
        if address_info is None:
            continue
        fax = address_info['faxAreaCode'] + '-' + address_info['faxNumber']
        name = address_info['name']
        city = address_info['city']
        state = address_info['state']
        search_results = yelp_api.search_query(term=name + ' prison', category_filter='publicservicesgovt', location=city + ',' + state)
        if len(search_results['businesses']) > 0:
            print json.dumps(search_results) + ','
#result = search_results['businesses'][0]
#for result in search_results['businesses']:
#    print result['name']


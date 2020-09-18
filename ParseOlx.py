import requests
import os
from bs4 import BeautifulSoup as BS
NEW_KEYS = []

class OlX:
    host = 'https://olx.kz'
    url = 'https://www.olx.kz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/'
    lastKey = []
    lastKey_file = ''
    def __init__(self):
        pass

   # проверяем новые посты
    def new_post(self, paramUrl='/petropavlovsk'):
        r = requests.get(self.url+paramUrl)
        print(r)
        html = BS(r.content, 'html.parser')
        new = []
        key_for_update = []
        items = html.find_all('a', class_=('marginright5'), href=True)
        for i in items:
            url = i['href']
            key = url[url.index('ID'):url.index('.html')]
            if key not in self.lastKey:
                print('new')
                new.append(url)
                key_for_update.append(key)
        if(new):
            self.update_keys(key_for_update)
            return new
        else:
            return False


    def get_lastKey(self, country='kostanay', KEYSI='ID123'):
        NEW_KEYS.clear()
        c = 0
        dataPosts = {}
        r = requests.get(self.url + country)
        html = BS(r.content, 'html.parser')
        item = html.find_all('a', class_=('marginright5'), href=True)
        costs = html.select('div p strong')[:-2]

        while c <= 43:
            price = costs[c].get_text()[:-4].replace(' ', '')
            url = item[c]['href']
            key = url[url.index('ID'):url.index('.html')]
            if key not in KEYSI:
                NEW_KEYS.append(key)
                print(key)
                dataPosts[c] = [key, int(price), url]
            c+=1
        return dataPosts


    def update_keys(self, newKeys):
        with open(self.lastKey_file, 'a') as f:
            for i in newKeys:
                self.lastKey.append(i)
                f.write(i + '\n')
        return None


    def post_info(self, posts):
        r = requests.get(posts)
        html = BS(r.content, 'html.parser')
        a = html.select('div h1')[0].get_text()
        b = html.select('.pricelabel__value')[0].get_text()
        c = html.select('.offer-details__value')[0].get_text()
        d = html.find_all('div', id='textContent')[0].get_text()
        e = html.select('div ul li em strong')[0].get_text()
        info = {
            'title': a,
            'prase':b,
            'who':c,
            'disc':d,
            'time':e,
            'url':posts
        }
        return info


if __name__ == '__main__':

    one = OlX('lastkeys222.txt')
    geton = one.new_post()
    print(one.lastKey)
    print(geton)

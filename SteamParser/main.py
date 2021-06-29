
from datetime import time
import requests
import json
import steam.webauth as wa
from user_agent import generate_user_agent
import time
import os
import sys
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH.replace('/SteamParser', ''))
os.environ['DJANGO_SETTINGS_MODULE'] = 'steamsite.settings'
import django
django.setup()
from SteamParser import models

from urllib.parse import urlencode
class SteamParser:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers = {'user-agent': generate_user_agent()}
        self.float_url = 'https://api.csgofloat.com'
        self.find_url = 'https://steamcommunity.com/market/search/render/'
        self.params_find = {'start': 0, 'count': 100, 'norender': 1, 'appid': 730, 'search_descriptions': 1}
        self.listing_url = 'https://steamcommunity.com/market/listings/730/{}/render/'
        self.price_url = 'https://steamcommunity.com/market/priceoverview/'
        self.params_price = {'appid':730, 'currency': 1, 'norender': 1}
        self.params_listing = {'start': 0, 'count': 100, 'currency': 1, 'norender': 1}
        self.image_url = 'https://community.cloudflare.steamstatic.com/economy/image/{}/150fx150x'
    def get_stickers_from_file(self) -> list:
        with open(PATH + '/1.txt', 'r') as f:
            data = f.read().split('\n')
            f.close()
        return data
    def get_listings(self, market_hash_name, sticker, count = 0) -> list:
        params = self.params_listing.copy()
        params.update({'filter': sticker})
        r = self.session.get(self.listing_url.format(market_hash_name), params = params)
        time.sleep(1)
        if r.ok:
            res = []
            if isinstance(r.json()['listinginfo'], list):
                return None
            for i, j in r.json()['listinginfo'].items():
                data = j['asset']['market_actions'][0]['link'].replace('%listingid%', j['listingid'])
                data = data.replace('%assetid%', j['asset']['id'])
                price = j['converted_price_per_unit'] + j['converted_fee_per_unit']
                res.append({'link': data, 'price': price})
            return res
        else:
            count+=1
            if count < 3:
                self.session.headers = {'user-agent': generate_user_agent()}
                print('get listings is sleeping 300 sec')
                time.sleep(300)
                return self.get_listings(market_hash_name, sticker, count)
            else:
                return None
    def get_price(self, market_hash_name):
        params = self.params_price.copy()
        params.update({'market_hash_name': market_hash_name})
        r = self.session.get(self.price_url, params = params)
        time.sleep(1)
        print(r.url)
        if r.ok:
            try:
                price = r.json()['median_price'].replace('$', '').replace('.', '')
                try:
                    price = price.replace(',', '')
                except:
                    pass
            except:
                try:
                    price = r.json()['lowest_price'].replace('$', '').replace('.', '')
                    try:
                        price = price.replace(',', '')
                    except:
                        pass
                except:
                    price = None
            return price
        else:
            self.session.headers = {'user-agent': generate_user_agent()}
            print('get price is sleeping 60 sec')
            time.sleep(60)
            return self.get_price(market_hash_name)
    def get_float(self, link):
        r = self.session.get(self.float_url, params = {'url': link})
        if r.ok:
            return {'float': r.json()['iteminfo']['floatvalue'], 'img': r.json()['iteminfo']['imageurl'], 'stickers': r.json()['iteminfo']['stickers']}
        else:
            self.session.headers = {'user-agent': generate_user_agent()}
            print('get float is sleeping 60 sec')
            time.sleep(60)
            return self.get_float(link)
    def get_sticker(self, name, stick_id):
        stick , created = models.Sticker.objects.get_or_create(name = name, sticker_id = stick_id)
        if created:
            params = {'query': name,'start': 0, 'count': 100, 'norender': 1, 'appid': 730}
            r = self.session.get(self.find_url, params = params)
            print(r.url)
            if r.ok:
                price = self.get_price('Sticker | ' + name)
                stick.price = price
                stick.icon_url = self.image_url.format(r.json()['results'][0]['asset_description']['icon_url'])
                stick.save()
                return {'url': self.image_url.format(r.json()['results'][0]['asset_description']['icon_url']), 'price': price}
            else:
                print('get sticker is sleeping 60 sec')
                time.sleep(60)
                return self.get_sticker(name, stick_id)
        else:
            return {'url': stick.icon_url, 'price': stick.price}
    def search_skins(self, stickers = None):
        if not stickers:
            stickers = self.get_stickers_from_file()
        for i, sticker in enumerate(stickers):
            params = self.params_find.copy()
            payload = urlencode(params).replace('?', '&')
            r = self.session.get(self.find_url+ '?query={}&category_730_ItemSet[]=any&category_730_Weapon[]=any&category_730_Quality[]=#p15_price_asc'.format(sticker), params = payload)
            time.sleep(1)
            if r.ok:
                _ = stickers.pop(i)
                data = r.json()['results'][1:]
                count = r.json()['total_count']
                if count > 100:
                    while count > 0:
                        time.sleep(10)
                        count = count - 100
                        params.update({'start': params['start'] + 100})
                        r = self.session.get(self.find_url, params = params)
                        try:
                            data.extend(r.json()['results'])
                        except:
                            pass
                for j in data:
                    listings = self.get_listings(j['hash_name'], sticker)
                    if not listings:
                        continue
                    for k in listings:
                        d = k.copy()
                        pricing, created = models.Item.objects.get_or_create(name = j['hash_name'])
                        if created:
                            price = self.get_price(j['hash_name'])
                            d.update({'default': price})
                            pricing.default = price
                            pricing.save()
                        else:
                            d.update({'default': pricing.default})
                        d.update(self.get_float(d['link']))
                        sticks = []
                        for q, y in enumerate(d['stickers']):
                            f = y.copy()
                            f.update(self.get_sticker(f['name'], f['stickerId']))
                            sticks.append(f)
                        d['stickers'] = sticks
                        d.update({'url': 'https://steamcommunity.com/market/listings/730/{}?filter={}'.format(j['hash_name'], sticker)})
                        d.update({'name': j['hash_name']})
                        dat = models.ItemJson(data = d)
                        dat.save()
                        print(d)
            else:
                self.session.headers = {'user-agent': generate_user_agent()}
                print('search skins is sleeping 300 sec')
                time.sleep(300)
                return self.search_skins(stickers)
pars = SteamParser()
pars.search_skins()
import datetime
import re
import unicodedata
import uuid
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import Session

import config


class Harvester:
    def __init__(self):
        conf = config.Config()
        self.telephone = conf.get('DataSources.Beetenders.Telephone')
        self.password = conf.get('DataSources.Beetenders.Password')
        self.host = conf.get('DataSources.Beetenders.Host')
        self.session: Session = requests.session()

    def login(self):
        self.session.post(
            f"{self.host}/api/signin",
            data={
                'telephone': self.telephone,
                'password': self.password,
            }
        )

    def get_page(self, page_number: int = 1, filters: dict = {}):
        filters = [f'{k}={v}' for k, v in filters.items()]
        filters = '&'.join(filters)
        url = self.host + '/annonces' \
              + ('?' if len(filters) > 0 and page_number != 1 else '') \
              + (f'page={page_number}' if page_number != 1 else '') \
              + filters

        response = self.session.get(url, timeout=20)
        return BeautifulSoup(response.text, 'html.parser')

    def get_boxes(self, soup: BeautifulSoup):
        boxes = soup.select('.boxes-list')
        return boxes

    def harvest_links(self, boxes: List[BeautifulSoup]) -> Tuple[DataFrame, List[List[str]]]:
        dataframe = DataFrame(columns=config.dataframe_cols.keys())\
            .astype(config.dataframe_cols)
        images_holder = []
        for index, box in enumerate(boxes):
            link = self.host + f'/{box.find('a').get('href').strip()}'
            response = self.session.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            announcement_types = self._get_types(box)
            business_lines = self._get_business_lines(box)
            pub_date = self._get_pub_date(box)
            due_date = self._get_due_date(box)

            page_data = self.harvest_page(soup)

            dataframe.loc[index] = {
                'id': str(uuid.uuid5(uuid.NAMESPACE_URL, link)),
                'wilaya': self._get_wilaya(box),
                'announcement_types': announcement_types,
                'business_lines': business_lines,
                'publish_date': pub_date.date(),
                'due_date': due_date.date(),
                'status': True,
                **page_data[0],
            }
            images_holder.append(page_data[1])

        return dataframe, images_holder

    def harvest_page(self, soup: BeautifulSoup) -> (dict, List[str]):
        _ = soup.select('.annonceur-left p')
        try:
            contact = '/'.join([
                _[0].text.strip() if '@' in _[0].text.strip() else '',
                _[1].text.strip() if '0' in _[1].text.strip() else ''
            ]).lstrip('/').rstrip('/')
        except:
            contact = ''

        _ = soup.select_one('span.desc-02')
        number = _.text.split(':')[1] if _ else ''

        description_box = soup.select_one('.description-box')
        owner_regex = re.compile(r'(?<=Annonceur : )(.* ?)+(?=\s)', re.IGNORECASE)
        due_amount_regex = re.compile(r'\d+(\.\d*)?(?= ?DZD)', re.IGNORECASE)
        owner = owner_regex.search(description_box.get_text())
        due_amount = due_amount_regex.search(description_box.get_text())

        images = [image.get('src') for image in soup.select('.gallery img')]
        data_dict = {
            'title': soup.find('h1').text.strip(),
            'number': number,
            'description': '',
            'contact': contact,
            'terms': '',
            'owner': owner[0] if owner else '',
            'due_amount': int(due_amount[0]) if due_amount else -1,
        }

        return data_dict, images

    @staticmethod
    def _get_wilaya(box: BeautifulSoup) -> int | None:
        _ = box.find(class_='offers_box')\
            .select_one('h2')\
            .stripped_strings
        _ = list(_)
        nfkd_form = unicodedata.normalize('NFKD', _[1])
        wilaya = "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

        return config.wilayas_dict.get(wilaya)

    @staticmethod
    def _get_types(box: BeautifulSoup) -> List[int]:
        type_text = box.find(class_='offers_box').find('span').text.strip()
        return config.type_dict.get(type_text)

    @staticmethod
    def _get_business_lines(box: BeautifulSoup) -> List[int]:
        business_lines = box.find(class_='offers_box').findNext('p').findAll('span')
        return list({
            config.business_lines_dict.get(element.text.strip(), 32)
            for element in business_lines
        })

    @staticmethod
    def _get_pub_date(box: BeautifulSoup) -> datetime.datetime:
        date_str = box.find(class_='offers_box').find_all('span')[1].text
        pub_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if pub_date > datetime.datetime.today():
            pub_date = datetime.datetime.today()
        return pub_date

    @staticmethod
    def _get_due_date(box: BeautifulSoup) -> datetime.datetime:
        date_str = box.find(class_='offers_box').find_all('span')[2].text
        return datetime.datetime.strptime(date_str, '%d-%m-%Y')

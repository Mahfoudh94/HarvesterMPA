import datetime
import re
import threading
import unicodedata
import uuid
from typing import List, Tuple, Set

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import Session
from tqdm import tqdm

import config
from logger import base_logger


class Harvester:
    _page_counter: int = 1
    stop_event = threading.Event()

    def __init__(self):
        conf = config.Config()
        self.telephone = conf.get('DataSources.Beetenders.Telephone')
        self.password = conf.get('DataSources.Beetenders.Password')
        self.host = conf.get('DataSources.Beetenders.Host')
        self.session: Session = requests.session()
        self.hash_list: Set[str] = set()
        self.re_encounters: int = 0

    @classmethod
    def page_count_iter(cls):
        base_logger.info(f"scrapping page {cls._page_counter}")
        cls._page_counter += 1
        return cls._page_counter - 1

    def login(self):
        self.session.post(
            f"{self.host}/api/signin",
            data={
                'telephone': self.telephone,
                'password': self.password,
            }
        )

    def get_page(self, page_number: int = None, filters: dict = None):
        if page_number is None:
            page_number = self.page_count_iter()
        if filters is None:
            filters = dict()

        filters = [f'{k}={v}' for k, v in filters.items()]
        filters = '&'.join(filters)
        url = self.host + '/annonces' \
              + ('?' if len(filters) > 0 or page_number != 1 else '') \
              + (f'page={page_number}' if page_number != 1 else '') \
              + filters

        response = None
        n_try = 1
        while response is None:
            if self.stop_event.is_set():
                return BeautifulSoup()
            try:
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                base_logger.warn(f"try: {n_try}, link: {url}\n" \
                + f"{e.__class__.__name__}: {e}")
                n_try += 1

        return BeautifulSoup(response.text, 'html.parser')

    def harvest_links(self, boxes: List[BeautifulSoup]) -> Tuple[DataFrame, List[List[str]]]:
        dataframe = DataFrame(columns=config.dataframe_cols.keys())\
            .astype(config.dataframe_cols)
        images_holder = []
        index = 0
        pbar = tqdm(total=len(boxes))

        for box in boxes:
            link = self.host + f'/{box.find('a').get('href').strip()}'
            link_hash = uuid.uuid5(uuid.NAMESPACE_URL, link)
            link_hash_string = str(link_hash)

            response = None
            n_try = 1
            while response is None:
                if self.stop_event.is_set():
                    break
                try:
                    response = self.session.get(link, timeout=20)
                except requests.exceptions.RequestException as e:
                    base_logger.warn(
                    f"link: {link}\n" \
                    + f"{e.__class__.__name__}: {e}"
                    )
                n_try += 1

            if self.stop_event.is_set():
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            announcement_types = self._get_types(box)
            business_lines = self._get_business_lines(box)
            pub_date = self._get_pub_date(box)
            due_date = self._get_due_date(box)

            if link_hash in self.hash_list:
                self.re_encounters += 1
                pbar.update(1)
                continue

            page_data = None
            try:
                page_data = self.harvest_page(soup)
            except Exception as e:
                base_logger.error(f"error scrapping page {link}:\n{e.__class__.__name__}: {e}")
                continue

            dataframe.loc[index] = {
                'id': link_hash_string,
                'wilaya': self._get_wilaya(box),
                'announcement_types': announcement_types,
                'business_lines': business_lines,
                'publish_date': pub_date.date(),
                'due_date': due_date.date(),
                'status': True,
                **page_data[0],
            }
            images_holder.append(page_data[1])
            index += 1
            pbar.update(1)

        pbar.close()
        return dataframe, images_holder

    @staticmethod
    def harvest_page(soup: BeautifulSoup) -> (dict, List[str]):
        item = soup.select('.annonceur-left p')
        try:
            contact = '/'.join([
                item[0].text.strip() if '@' in item[0].text.strip() else '',
                item[1].text.strip() if '0' in item[1].text.strip() else ''
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
    def get_boxes(soup: BeautifulSoup):
        boxes = soup.select('.boxes-list')
        return boxes

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

from enum import Enum
from typing import Union, List
import requests
import csv


class API(Enum):

    ALGOEXPLORER = "https://indexer.algoexplorerapi.io/rl/v1/transactions"
    ALGOSCAN = "https://algoscan.app/api/transactions/"

class Scrapper:

    def __init__(self, api: API):
        self.api = api
        self.api_base_url = api.value
    
    def get_data(self, address: str, pages: Union[int, None]=None) -> List:
        try:
            if self.api == API.ALGOSCAN:
                return self._algoscan(address, pages)
            else:
                return self._algoexplorer(address, pages)
        except Exception as e:
            print(f'Error Fetching Transaction Data: {e}')
            return []
        
    def _algoscan(self, address: str, pages: Union[int, None]=None) -> List:
        """
        Makes a request to algoScan API to fetch transaction data for the given address.

        Args:
            - address: desired address for transaction data
            - pages: desired number of pages for response[can be skipped to fetch all pages]
        Returns:
            - List[{}]: A list of transaction data for the given address
        """
        data = []
        offset = 0
        page = 0
        while True:
            if pages:
                if page == pages:
                    break
            res = requests.get(f"{self.api_base_url}{address}?offset={offset}")
            dat = res.json()
            if dat == []:
                break
            data.extend(list(map(lambda item: {'from': item['sender'], 'amount': item['amount']}, dat)))
            page += 1
            offset += 20
        return data

    def _algoexplorer(self, address: str, pages: Union[int, None]=None):
        """
        Makes a request to algoExplorer API to fetch transaction data for the given address.

        Args:
            - address: desired address for transaction data
            - pages: desired number of pages for response[can be skipped to fetch all pages]
        Returns:
            - List[{}]: A list of transaction data for the given address
        """
        page = 1
        limit = 50
        data = []
        while True:

            if pages:
                if page == pages:
                    break
            url = f"{self.api_base_url}?page={page}&limit={limit}&address={address}"
            resp = requests.get(url)
            try:
                dat = resp.json()['transactions']
            except Exception as e:
                break
            data.extend(list(map(lambda item: {'from': item['sender'], 'amount': item['asset-transfer-transaction']['amount']} if item.get('asset-transfer-transaction', None) else {'from': item['sender'], 'amount': item['payment-transaction']['amount']}, dat)))
            page += 1
        return data

    def write_to_csv(self, data: List, output_file: str):
        if not data:
            print('Empty Data')
            return
        keys = data[0].keys()
        with open(output_file, 'w', newline='') as file:
            dict_writer = csv.DictWriter(file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)  





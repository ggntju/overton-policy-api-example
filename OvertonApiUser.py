from dotenv import load_dotenv
import requests
import os
import pandas as pd

class OvertonApiUser:
    def __init__(self, query: str):
        load_dotenv()
        self.api_key = os.getenv('OVERTON_API_KEY')
        self.query = query
        self.base_url = "https://app.overton.io/documents.php"
        self.output_format = "json"
        self.initialized = False
        self.next_page_url = ""
        self.next_page_index = 0
        self.total_pages = 0

    def initialRequest(self):
        payload = {
            "api_key": self.api_key,
            "query": self.query,
            "format": self.output_format
        }

        r = requests.get(self.base_url, params=payload)
        response = r.json()
        print("processing page 1 ...")
        self.next_page_url, self.next_page_index = self.__process_response(response, 1, True)
        if(self.next_page_url != "" and self.next_page_index != 0):
            self.initialized = True

    def nextRequest(self) -> bool:
        if(self.initialized):
            r = requests.get(self.next_page_url)
            response = r.json()
            print("processing page " + str(self.next_page_index) + " of " + str(self.total_pages) + "...")
            self.next_page_url, self.next_page_index = self.__process_response(response, self.next_page_index, True)
            if(self.next_page_url == ""):
                return True
            else:
                return False
        else:
            print("Not initialized")
            return False

    def __process_response(self, response: dict, page_index: int, output_flag: bool) -> [str, int]:
        next_page_url = ""
        page_df = pd.DataFrame()
        try:
            query = response["query"]
            self.total_pages = query["pages"]
            next_page_url = query["next_page_url"]
        except:
            message = "query not found in page index " + str(page_index)
            print(message)

        try:
            facets = response["facets"]
        except:
            message = "facets not found in page index " + str(page_index)
            print(message)

        try:
            results = response["results"]
            for result in results:
                df = pd.DataFrame.from_dict(result, orient='index').transpose()
                page_df = pd.concat([page_df, df])
        except:
            message = "results not found in page index " + str(page_index)
            print(message)  

        page_df.to_excel("page_" + str(page_index) + ".xlsx", index=False)
        return [next_page_url, page_index + 1]
from dotenv import load_dotenv
import requests
import os
import pandas as pd

class OvertonApiUser:
    def __init__(self, query: str):
        load_dotenv()
        self.__api_key = os.getenv('OVERTON_API_KEY')
        self.__query = query
        self.__base_url = "https://app.overton.io/documents.php"
        self.__output_format = "json"
        self.__initialized = False
        self.__next_page_url = ""
        self.__next_page_index = 0
        self.__total_pages = 0

    def initialRequest(self):
        payload = {
            "api_key": self.__api_key,
            "query": self.__query,
            "format": self.__output_format
        }

        try:
            r = requests.get(self.__base_url, params=payload)
            response = r.json()
            print("processing page 1 ...")
            self.__next_page_url, self.__next_page_index = self.__process_response(response, 1, True)
            if(self.__next_page_url != "" and self.__next_page_index != 0):
                self.__initialized = True
        except:
            print("initial request failed")

    def nextRequest(self) -> bool:
        if(self.__initialized):
            try:
                r = requests.get(self.__next_page_url)
                response = r.json()
                print("processing page " + str(self.__next_page_index) + " of " + str(self.__total_pages) + "...")
                self.__next_page_url, self.__next_page_index = self.__process_response(response, self.__next_page_index, True)
                if(self.__next_page_url == ""):
                    return True
                else:
                    return False
            except:
                print("next request failed")
                return False
        else:
            print("Not initialized")
            return False

    def __process_response(self, response: dict, page_index: int, output_flag: bool) -> [str, int]:
        next_page_url = ""
        page_df = pd.DataFrame()
        try:
            query = response["query"]
            self.__total_pages = query["pages"]
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

        if(output_flag):
            try:
                page_df.to_excel("page_" + str(page_index) + ".xlsx", index=False)
            except:
                message = "failed to output page index " + str(page_index)
                print(message)
                
        return [next_page_url, page_index + 1]
from dotenv import load_dotenv
import requests
import os
import pandas as pd
import logging

class OvertonApiUser:
    def __init__(self, query: str, year: int = 0, has_references:bool = None):
        load_dotenv()
        self.__logger = logging.getLogger(__name__)
        logging.basicConfig(filename='overton-api.log', encoding='utf-8', level=logging.WARNING)
        self.__api_key = os.getenv('OVERTON_API_KEY')
        self.__query = query
        self.__year = year
        self.__has_references = has_references
        self.__base_url = "https://app.overton.io/documents.php"
        self.__output_format = "json"
        self.__initialized = False
        self.__next_page_url = ""
        self.__next_page_index = 0
        self.__total_pages = 0


    def initialRequest(self) -> bool:
        payload = {}
        if(self.__year == 0 and self.__has_references == None): 
            payload = {
                "api_key": self.__api_key,
                "query": self.__query,
                "format": self.__output_format
            }
        if(self.__year != 0 and self.__has_references == None):
            payload = {
                "api_key": self.__api_key,
                "query": self.__query,
                "year": self.__year,
                "format": self.__output_format
            }
        if(self.__year == 0 and self.__has_references != None):
            payload = {
                "api_key": self.__api_key,
                "query": self.__query,
                "has_references": self.__has_references,
                "format": self.__output_format
            }
        if(self.__year != 0 and self.__has_references != None):
            payload = {
                "api_key": self.__api_key,
                "query": self.__query,
                "has_references": self.__has_references,
                "format": self.__output_format,
                "year": self.__year,
            }

        try:
            r = requests.get(self.__base_url, params=payload)
            response = r.json()
            self.__next_page_url, self.__next_page_index = self.__process_response(response, 1, True)
            if(self.__next_page_index != 0):
                self.__initialized = True
            
            print("processing page 1 ... of " + str(self.__total_pages) + "...")
            return True
        except:
            print("initial request failed")
            message = "initial request failed on query " + self.__query + " year " + str(self.__year) + " has_references " + str(self.__has_references)
            self.__logger.error(message)
            return False
        
        return False

    def nextRequest(self) -> bool:
        if(self.__initialized):
            if(self.__next_page_url == False):
                print("no more pages")
                return True
            try:
                r = requests.get(self.__next_page_url)
                response = r.json()
                
                self.__next_page_url, self.__next_page_index = self.__process_response(response, self.__next_page_index, True)
                if(self.__next_page_url == False):
                    return True
                else:
                    return False
            except:
                print("next request failed")
                message = "next request failed on query " + self.__query + " year " + str(self.__year) + " has_references " + str(self.__has_references) + " next page index " + str(self.__next_page_index)
                self.__logger.error(message)
                return False
        else:
            print("Not initialized")
            message = "Not initialized on query " + self.__query + " year " + str(self.__year) + " has_references " + str(self.__has_references)
            self.__logger.error(message)
            return True

    def __process_response(self, response: dict, page_index: int, output_flag: bool):
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
            if(self.__total_pages == 0):
                message = "total pages is 0"
                print(message)
                return [False, 0]
            try:
                filename = ""
                if(self.__year == 0 and self.__has_references == None):
                    filename = "page_" + str(page_index) + "_query_" + self.__query + ".xlsx"
                if(self.__year != 0 and self.__has_references == None):
                    filename = "year_" + str(self.__year) + "_page_" + str(page_index) + "_query_" + self.__query + ".xlsx"
                if(self.__year != 0 and self.__has_references != None):
                    filename = "year_" + str(self.__year) + "_page_" + str(page_index) + "_query_" + self.__query + "_has_references_" + str(self.__has_references) + ".xlsx"
                page_df.to_excel("./results/" + filename, index=False)
            except:
                message = "failed to output page index " + str(page_index)
                print(message)
                
        return [next_page_url, page_index + 1]
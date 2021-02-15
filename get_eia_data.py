import json
import numpy as np
import pandas as pd
from dateutil import parser
import datetime
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


class EIAgov(object):
    def __init__(self, token, series):
        """Initialize the data portal object

        Args:
            token (str): API Key from EIA
            series (str): Series ID. Can find more information at https://www.eia.gov/opendata/qb.php.
        """
        self.token = token
        self.series = series

    def __repr__(self):
        return "EIAgov({}, {})".format(self.token, self.series)

    def get_raw_data(self, ser=None):
        """Querys EIA's API for a raw string with the data series ID.

        Args:
            ser (str, optional): EIA Series ID, if None uses self.series. Defaults to None.

        Returns:
            dict: json parsed dictionary from EIA string
        """
        if not ser:
            ser = self.series
        url = f"http://api.eia.gov/series/?api_key={self.token}&series_id={ser}"
    
        try:
            # Get response from EIA
            response = urlopen(url)
            raw_byte = response.read()
            # ensure string is in correct encoding
            raw_string = str(raw_byte, 'utf-8-sig')
            # load data with json files
            jso = json.loads(raw_string)
            return jso
        except HTTPError as e:
            print('HTTP error type.')
            print('Error code:', e.code)
        except URLError as e:
            print('URL type error.')
            print('Reason: ', e.reason)
    
    def get_formatted_data(self, ser=None):
        """Wrapper to get data from EIA and format it in a pandas DataFrame.
        Should be used most of the time to get data.

        Args:
            ser (str, optional): EIA Series ID, if None uses self.series. Defaults to None.

        Returns:
            pandas.DataFrame: DataFrame with the results from EIA on the series provided
        """
        if not ser:
            ser = self.series
        raw_data = self.get_raw_data(ser)
        formatted = self.format_data(raw_data)
        return formatted

    def format_data(self, data):
        """Function to parse date and construct a dataframe from the raw data from EIA

        Args:
            data (dict): JSON parsed dictionary from self.get_raw_data

        Returns:
            pandas.DataFrame: DataFrame with the results from EIA on the series provided
        """
        try:
            date_series = data['series'][0]['data']
        except KeyError as e:
            print("Key Error for series_id ", self.series)
            # returning an empty data frame so users can use 
            # pd.DataFrame().empty() as a conditional
            return pd.DataFrame()
        
        # record information about the retrieved data series
        with open("series_records.json", "r") as records_file:
            records = json.load(records_file)
        
        records[data["series"][0]["series_id"]] = {
            "name":data["series"][0]["name"],
            "description":data["series"][0]["description"],
            "start":data["series"][0]["start"],
            "end":data["series"][0]["end"]
        }

        with open("series_records.json", "w") as records_file:
            json.dump(records, records_file)

        # grab the units
        unit = data['series'][0]['units']
        # intermediate data containers
        date = []
        data_series = []
        units = []
        #* This is the most janky part of the entire program.
        #* I am trying to parse the dates provided by EIA, but it may not work. 
        for date_item, data_item in date_series:
            if date_item[-1] == "Z":
                date_item = date_item[:-1] + "UTC"
            # Datetime format strings. 
            # You can add strings to this list that to parse whatever datetime format
            # your data series is reported in
            formats = ["%Y", "%Y%m", "%Y%m%dT%H%Z", "%Y%m%dT%H%z", None]
            for j, fmt in enumerate(formats):
                if not fmt:
                    print('Failed stripping datetime from string')
                    print('String example: ', date_item)
                    break
                try:
                    if j == 3:
                        string = date_item +"00"
                    else:
                        string = date_item
                    dt = datetime.datetime.strptime(string, fmt)
                    dt_str = dt.strftime("%Y-%m-%d %H:%M")
                    date.append(dt_str)
                    data_series.append(data_item)
                    units.append(unit)
                    break
                except ValueError as e:
                    # basically, if something fails when parsing a date, 
                    # we want to continue instead of fail.
                    pass
        
        # create a dataframe of the results
        df = pd.DataFrame(data=[date, data_series, units]).transpose()
        df.columns = ['Date', 'Data', 'Units']

        return df


if __name__ == '__main__':
    import sys
    # parse args from command line
    try:
        series_id = sys.argv[1]
    except IndexError as e:
        print('Index error accessing command line arguments.\n')
        print("Usage:")
        print("$ python get_eia_data.py <EIA API Series ID>\n")
        print("e.g. $ python get_eia_data.py ELEC.GEN.NG-US-99.M")
        sys.exit()

    # grab the api-key, this needs to be populated with your api_key
    # can find more information here https://www.eia.gov/opendata/qb.php.    
    with open('./api_key.txt', 'r') as key_file:
        api_key = key_file.read().strip("\n\r")

    data = EIAgov(api_key, series_id)
    print('Getting data for: ', series_id)
    df = data.get_formatted_data()
    print('Writing data to file: ', series_id + '.csv')
    df.to_csv(series_id + '.csv')

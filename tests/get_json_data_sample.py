
# AUTHOR: @SmileBar
# DESCRIPTION: Simple script to iterate through json data samples.
# 

import json
import os

data_path = os.path.join(os.path.dirname(__file__),'..','data', 'prize.json')

def read_json(path):
    file = open(path,'r')
    data = json.load(file)
    file.close()
    return data

def filter_prize_by_year(data:dict, from_year, to_year):
    return [prize for prize in data['prizes'] 
            if from_year <= int(prize['year']) <= to_year]

def main():
    # Fetch Nobel Prize data locally
    data = read_json(data_path)
    # Extracting prize data for years 2013 to 2023
    filtered_prizes = filter_prize_by_year(data,2013,2023)
    
    
    # Print data
    for prize in filtered_prizes:
        print(prize)
        print("\n")
   

if __name__ == "__main__":
    main()
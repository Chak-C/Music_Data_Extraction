import requests
from bs4 import BeautifulSoup
import csv
import tqdm

class VocalGender():
    def search_gender(self, artist):
        request_url = f"https://musicbrainz.org/search?query={artist}&type=artist&method=indexed"

        response = requests.get(request_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = soup.find('div', class_ = 'fullwidth').find('table',class_='tbl')
            
            row_number = 1 # 0 is header
            while row_number < 20:
                try:
                    row = results.find_all('tr')[row_number].find_all('td')
                except IndexError:
                    return None
                
                if row[2].get_text().strip() == 'Person':
                    gender = row[3].get_text().strip()

                    if gender:
                        return gender
                    else:
                        row_number += 1
                        continue
                else: # if group or no type, next
                    row_number += 1
                    continue
            else:
                print('Information not found in response.')
        else:
            print(f"Error retrieving data, status code: {response.status_code}")
             
        return None

FILE_PATH = 'C:\\Users\\Alvis\\Desktop\\Music\\BI\\Extraction\\output\\artist.csv'
tr = VocalGender()

data = []
new_data = []

with open(FILE_PATH, 'r', encoding='utf-8', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        data.append(row)

for row in tqdm.tqdm(data): 
    try:
        gender = tr.search_gender(row[0])
        new_data.append([row[0], gender])
    except:
        new_data.append([row[0], None])

file.close()

with open(FILE_PATH, 'w', encoding='utf-8', newline = '') as file:
    writer = csv.writer(file)
    writer.writerow(['artist','gender'])

    for row in new_data:
        writer.writerow(row)


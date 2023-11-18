import requests
from bs4 import BeautifulSoup
import pandas as pd

def categorize_publication(h1_title, panel_heading):
    lower_h1_title = h1_title.lower()
    lower_panel_heading = panel_heading.lower()
    
    if 'barometer' in lower_h1_title:
        return 'Survey-report'
    elif 'notat' in lower_h1_title:
        return 'Memorandum'
    elif 'baggrundspapir' in lower_panel_heading:
        return 'Backgrounder'
    elif 'rapport' in lower_panel_heading or 'report' in lower_panel_heading:
        return 'Report'
    else:
        return 'Other'

base_url = "https://cms.polsci.ku.dk"
url = base_url + "/publikationer/"

response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    publication_data = []

    publications = soup.find_all('li', class_='media')

    for pub in publications:
        title = pub.find('h3', class_='media-heading').text.strip() if pub.find('h3', class_='media-heading') else ''
        pub_date = pub.find('div', class_='nyhedsliste_dato').span.text.strip() if pub.find('div', class_='nyhedsliste_dato') else ''
        link = pub.find('a', class_='legacy-tile-link')['href'] if pub.find('a', class_='legacy-tile-link') else ''
        
        pub_type = 'Not Available'
        if link:
            subpage_response = requests.get(base_url + link)
            if subpage_response.status_code == 200:
                subpage_soup = BeautifulSoup(subpage_response.content, 'html.parser')
                h1_title_element = subpage_soup.find('h1', class_='title')
                h1_title_text = h1_title_element.get_text() if h1_title_element else ''
                panel_heading = subpage_soup.find('div', class_='panel-heading')
                panel_heading_text = panel_heading.get_text() if panel_heading else ''
                pub_type = categorize_publication(h1_title_text, panel_heading_text)
            else:
                pub_type = 'Failed to Retrieve'
        else:
            pub_type = 'Link Not Found'

        publication_data.append({
            'Title': title,
            'Publication Date': pub_date,
            'Type': pub_type
        })

    df = pd.DataFrame(publication_data)
    df.to_excel('publications.xlsx', index=False)
    print("Data extracted and saved to publications.xlsx")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)

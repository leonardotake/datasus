import os
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def download_csv(url_csv, filename):
    if not os.path.exists(filename):
        csv_req = requests.get(url_csv)
        if csv_req.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(csv_req.content)
            print(f"Arquivo {filename} baixado com sucesso!")

def get_dataset_urls(dataset_url) -> dict: 

    if not os.path.exists(dataset_url):
        os.makedirs(dataset_url)

    base_url = "https://opendatasus.saude.gov.br/"
    dict_links = {}
    with requests.session() as session:
        dataset_page_url = base_url + dataset_url
        req = session.get(dataset_page_url)
        if req.status_code == 200:
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            dataset_section = soup.find('section', id='dataset-resources', class_='resources')
            if dataset_section:
                links = dataset_section.find_all('a', href=True)
                for link in links:
                    if "#" in link['href']:
                        continue
                    if "pdf" in link['href']:
                        continue
                    url = base_url + link['href']
                    req = session.get(url)
                    if req.status_code == 200:
                        html = req.text
                        soup = BeautifulSoup(html, 'html.parser')
                        module_section = soup.find('section', class_='module module-resource')
                        if module_section:
                            links = module_section.find_all('a', href=True)
                            for link in links:
                                url_csv = link['href']
                                if url_csv.endswith('.csv'):
                                    title_name = link.text
                                    dict_links[title_name] = url_csv
    return dict_links

def load_csv(dataset_path) -> pd.DataFrame:
    folder_path = Path(dataset_path)
    csv_files = folder_path.glob('*.csv')

    dfs = []
    for csv_file in csv_files:
        print(csv_file)
        df = pd.read_csv(csv_file, sep=";", low_memory=True, on_bad_lines="warn")
        dfs.append(df)

    # Concatenar os DataFrames se necessário
    combined_df = pd.concat(dfs)

    return combined_df

def main():
    dataset_url = "dataset/notificacoes-de-sindrome-gripal-leve-2023"

    dict_urls = get_dataset_urls(dataset_url)

    with ThreadPoolExecutor(max_workers=len(dict_urls)) as executor:
        for title, url in dict_urls.items():
            filename = f"{dataset_url}/{title}.csv"
            executor.submit(download_csv, url, filename)
    
    datasus_df = load_csv(dataset_url)
    

if __name__ == "__main__":
    main()

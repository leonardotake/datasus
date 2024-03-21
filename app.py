import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor

def download_csv(url, session):
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
                    title_name = link.text.strip()
                    filename = f'data/{title_name}.csv'
                    if not os.path.exists(filename):
                        csv_req = session.get(url_csv)
                        if csv_req.status_code == 200:
                            with open(filename, 'wb') as f:
                                f.write(csv_req.content)
                            print(f"Arquivo {filename} baixado com sucesso!")
                        else:
                            print(f"Falha ao baixar o arquivo CSV de {url_csv}")
        else:
            print("Seção de módulo não encontrada")
    else:
        print(f"Falha ao acessar a URL: {url}")

def main():
    base_url = "https://opendatasus.saude.gov.br"
    dataset_url = "/dataset/notificacoes-de-sindrome-gripal-leve-2023"

    # Criando o diretório 'data' se ele não existir
    if not os.path.exists('data'):
        os.makedirs('data')

    with requests.session() as session:
        dataset_page_url = base_url + dataset_url
        req = session.get(dataset_page_url)
        if req.status_code == 200:
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            dataset_section = soup.find('section', id='dataset-resources', class_='resources')
            if dataset_section:
                links = dataset_section.find_all('a', href=True)
                with ThreadPoolExecutor(max_workers=len(links)) as executor:
                    for link in links:
                        url = base_url + link['href']
                        executor.submit(download_csv, url, session)
            else:
                print("Seção de dataset não encontrada")
        else:
            print(f"Falha ao acessar a página do dataset: {dataset_page_url}")

if __name__ == "__main__":
    main()



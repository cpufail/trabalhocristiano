#Mostrar qual o site(s) utilizou * Steam lista dos mais populares
#Qual algoritmo de ordenação e por quê escolheu * Heapsort usando heapmin pq a gente ordenou em ordem crescente
#Qual linguagem de programação usou
#Qual biblioteca utilizada e por quê 

import os # Manipular arquivos
import heapq # Heapsort importado
import requests # Requisiçoes http
from bs4 import BeautifulSoup # Extração de dados


def scrape_steam_store():
    base_url = "https://store.steampowered.com/search/?category1=998"
    page = 1
    products = []

    while page < 10:  
        url = f"{base_url}&page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        
        items = soup.find_all('a', class_='search_result_row')
        if not items:
            break  

        for item in items:
            name = item.find('span', class_='title').text.strip()
            price_tag = item.find('div', class_='discount_final_price')
            if price_tag:
                price_text = price_tag.get_text().strip()

                
                if 'R$' in price_text:
                    price_text = price_text.split('R$')[-1].strip()
                    price = float(price_text.replace(',', '.').replace('R$', '').strip())
                else:
                    price = 0.00  
            else:
                price = 0.00  

            products.append((name, price))

        page += 1

    return products

def save_chunk(products, chunk_id):
    filename = f"chunk_{chunk_id}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for product in products:
                file.write(f"{product[0]}||{product[1]:.2f}\n")
        print(f"Chunk salvo: {filename}")
    except Exception as e:
        print(f"Erro ao salvar chunk: {e}")
    return filename

def read_chunk(file):
    products = []
    try:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                name, price = line.strip().split('||')
                products.append((name, float(price)))
        print(f"Chunk lido: {file}")
    except Exception as e:
        print(f"Erro ao ler chunk: {e}")
    return products


def merge_sorted_chunks(chunks, output_file):
    iterators = [iter(read_chunk(chunk)) for chunk in chunks]

    with open(output_file, 'w', encoding='utf-8') as out:
        min_heap = []
        for i, it in enumerate(iterators):
            try:
                product = next(it)
                heapq.heappush(min_heap, (product[1], i, product))
            except StopIteration:
                pass

        while min_heap:
            price, idx, product = heapq.heappop(min_heap)
            out.write(f"{product[0]}||{product[1]:.2f}\n")

            try:
                next_product = next(iterators[idx])
                heapq.heappush(min_heap, (next_product[1], idx, next_product))
            except StopIteration:
                pass


def external_merge_sort(products, chunk_size, output_file):
    chunks = []
    for i in range(0, len(products), chunk_size):
        chunk = products[i:i + chunk_size]
        chunk_sorted = sorted(chunk, key=lambda x: x[1])  
        chunk_file = save_chunk(chunk_sorted, len(chunks))
        chunks.append(chunk_file)

    merge_sorted_chunks(chunks, output_file)

    
    for chunk in chunks:
        os.remove(chunk)


if __name__ == "__main__":
    produtos = scrape_steam_store()

    chunk_size = 100
    output_file = "produtos_ordenados.txt"


    external_merge_sort(produtos, chunk_size, output_file)

    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            name, price = line.strip().split('||')
            print(f"Nome: {name}, Preço: R$ {float(price):.2f}")

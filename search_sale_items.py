import json

# Load items from sale_items.json
def load_items(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def search_items(items, name=None, min_price=None, max_price=None):
    results = []
    for item in items:
        match = True
        if name and name.lower() not in item['name'].lower():
            match = False
        if min_price is not None and float(item['price']) < min_price:
            match = False
        if max_price is not None and float(item['price']) > max_price:
            match = False
        if match:
            results.append(item)
    return results

def print_results(results):
    if not results:
        print('No items found.')
        return
    for item in results:
        print(f"ID: {item['id']}")
        print(f"Name: {item['name']}")
        print(f"Description: {item.get('description', 'N/A')}")
        print(f"Price: ${item['price']}")
        print(f"Image: {item.get('image', 'N/A')}")
        print('-' * 40)

def main():
    items = load_items('sale_items.json')
    print('Search items for sale:')
    name = input('Search by name (leave blank to skip): ').strip() or None
    min_price = input('Minimum price (leave blank to skip): ').strip()
    max_price = input('Maximum price (leave blank to skip): ').strip()
    min_price = float(min_price) if min_price else None
    max_price = float(max_price) if max_price else None
    results = search_items(items, name=name, min_price=min_price, max_price=max_price)
    print_results(results)

if __name__ == '__main__':
    main()

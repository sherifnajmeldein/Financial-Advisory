import requests
from requests.exceptions import RequestException

COINPAPRIKA_API_URL = 'https://api.coinpaprika.com/v1'
COINPAPRIKA_SEARCH_URL = f'{COINPAPRIKA_API_URL}/search'
COINPAPRIKA_TICKER_URL = f'{COINPAPRIKA_API_URL}/tickers'

def search_coin_by_name(coin_name):
    try:
        # Make a request to search for the coin by name
        params = {'q': coin_name}
        headers = {'Accept': 'application/json'}
        
        response = requests.get(COINPAPRIKA_SEARCH_URL, params=params, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        
        data = response.json()
        if 'currencies' in data and len(data['currencies']) > 0:
            # Assuming the first result is the most relevant
            coin_id = data['currencies'][0]['id']
            return coin_id
        else:
            print(f"Coin '{coin_name}' not found.")
            return None

    except RequestException as e:
        print(f"Error searching for coin '{coin_name}': {e}")
        return None

def get_crypto_price(coin_name):
    try:
        # First, search for the coin ID using the coin name
        coin_id = search_coin_by_name(coin_name)
        
        if coin_id:
            # Construct the URL to fetch ticker information
            url = f"{COINPAPRIKA_TICKER_URL}/{coin_id}"

            # Make the request to get the ticker information
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            
            data = response.json()
            if 'quotes' in data and 'USD' in data['quotes']:
                # Extract the price
                price = data['quotes']['USD']['price']
                return price
            else:
                print(f"Price information not found for '{coin_name}'.")
                return None
        else:
            print(f"Failed to retrieve coin ID for '{coin_name}'.")
            return None

    except RequestException as e:
        print(f"Error retrieving price for '{coin_name}': {e}")
        return None

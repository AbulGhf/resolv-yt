from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone
import os
from boost_checker import check_boosts


# Get the current directory of the Python file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask with correct template and static folders
app = Flask(__name__, 
         template_folder=os.path.join(current_dir, 'templates'),
         static_folder=os.path.join(current_dir, 'static'))

# Get API keys from environment variables
BASE_API_KEY = os.environ.get('BASE_API_KEY', 'ZIFYVT836FXTEGSRYMDZDAI6KM7BQUQE64')
ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY', 'GHA86RPT9HPEQZQEUD3QPFC827796KCJ4V')

TOKENS = [
    {   # Ethereum Pendle USR YT
        'name': 'Ethereum Pendle USR YT',
        'contracts': ['0xe0e034aff49755e80b15594ce3a16d74d1a09b2f'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 20, 'end_date': '2025-01-31'},
            {'rate': 15, 'end_date': '2025-02-22'}
        ],
        'maturity_date': '2025-02-22'
    },
    {   # Base Pendle USR YT
        'name': 'Base Pendle USR YT',
        'contracts': ['0x22cf19b7d8de1b53bbd9792e12ea86191985731f'],
        'api_key': BASE_API_KEY,
        'base_url': 'https://api.basescan.org/api',
        'points_schedule': [
            {'rate': 60, 'end_date': '2025-02-23'},
            {'rate': 45, 'end_date': '2025-04-24'}
        ],
        'maturity_date': '2025-04-24'
    },
    {   # Ethereum Spectra USR YT
        'name': 'Ethereum Spectra USR YT',
        'contracts': ['0x861e65f1bf472ead79c248111d78211907130820'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 20, 'end_date': '2025-01-31'},
            {'rate': 15, 'end_date': '2025-02-22'}
        ],
        'maturity_date': '2025-02-22'
    },
    {   # RLP Spectra YT
        'name': 'RLP Spectra YT',
        'contracts': ['0x4eaFef6149C5B0c3E42fF444F79675B3E3125cb7'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 45, 'end_date': '2025-02-23'},
            {'rate': 30, 'end_date': '2025-06-26'}
        ],
        'maturity_date': '2025-06-26'
    },
    {   # Spectra wstUSR YT (June 2025)
        'name': 'Spectra wstUSR YT',
        'contracts': ['0xb98b2C86243d742Bd54c59B04976C519d0a93ba1'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 30, 'end_date': '2025-02-22'},
            {'rate': 15, 'end_date': '2025-06-26'}
        ],
        'maturity_date': '2025-06-26'
    },
    {   # Spectra USR YT (Combined)
        'name': 'Spectra USR YT (Combined)', 
        'contracts': [
            '0x51C002aBe20bD7C5072cf96Ba979562E42700F20',
            '0xb98b2C86243d742Bd54c59B04976C519d0a93ba1'
        ],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 60, 'end_date': '2025-02-23'},
            {'rate': 45, 'end_date': '2025-04-30'}
        ],
        'maturity_date': '2025-04-30'
    },
    {   # Base USR LP (New Entry)
        'name': 'Base USR LP',
        'contracts': ['0xE15578523937ed7F08E8F7a1Fa8a021E07025a08'],
        'api_key': BASE_API_KEY,
        'base_url': 'https://api.basescan.org/api',
        'points_schedule': [
            {'rate': 60, 'end_date': '2025-02-23'},
            {'rate': 45, 'end_date': '2025-04-24'}
        ],
        'maturity_date': '2025-04-24',
        'price_api': 'https://api-v2.pendle.finance/core/v1/8453/assets/prices?addresses=0xE15578523937ed7F08E8F7a1Fa8a021E07025a08'
    },
    {   # Ethereum wstUSR LP (New Entry)
        'name': 'Ethereum wstUSR LP',
        'contracts': ['0x353d0B2EFB5B3a7987fB06D30Ad6160522d08426'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 30, 'end_date': '2025-02-22'},
            {'rate': 15, 'end_date': '2025-03-25'}
        ],
        'maturity_date': '2025-03-25',
        'price_api': 'https://api-v2.pendle.finance/core/v1/1/assets/prices?addresses=0x353d0B2EFB5B3a7987fB06D30Ad6160522d08426'
    },
    {   # USR on Ethereum
        'name': 'Ethereum USR',
        'contracts': ['0x66a1e37c9b0eaddca17d3662d6c05f4decf3e110'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 30, 'end_date': '2100-01-01'}  # 30 points/day indefinitely
        ],
        'maturity_date': '2100-01-01'  # Far future placeholder
    },
    {   # USR on Base
        'name': 'Base USR',
        'contracts': ['0x35E5dB674D8e93a03d814FA0ADa70731efe8a4b9'],
        'api_key': BASE_API_KEY,
        'base_url': 'https://api.basescan.org/api',
        'points_schedule': [
            {'rate': 30, 'end_date': '2100-01-01'}  # 30 points/day indefinitely
        ],
        'maturity_date': '2100-01-01'
    },
    {   # RLP on Ethereum
        'name': 'Ethereum RLP',
        'contracts': ['0x4956b52aE2fF65D74CA2d61207523288e4528f96'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 10, 'end_date': '2100-01-01'}  # 10 points/day indefinitely
        ],
        'maturity_date': '2100-01-01'
    },
    {   # RLP on Base
        'name': 'Base RLP',
        'contracts': ['0xC31389794Ffac23331E0D9F611b7953f90AA5fDC'],
        'api_key': BASE_API_KEY,
        'base_url': 'https://api.basescan.org/api',
        'points_schedule': [
            {'rate': 10, 'end_date': '2100-01-01'}  # 10 points/day indefinitely
        ],
        'maturity_date': '2100-01-01'
    },
        {   # STUSR
        'name': 'STUSR',
        'contracts': ['0x6c8984bc7DBBeDAf4F6b2FD766f16eBB7d10AAb4'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 5, 'end_date': '2025-12-31'}  # 5 points daily per 1 STUSR
        ],
        'maturity_date': '2025-12-31'
    }
]

SECONDS_PER_DAY = 86400

def format_timestamp(ts):
    """Convert timestamp to human-readable date."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')

def get_all_transfers(base_url, contracts, user_address, api_key):
    """Fetch all token transfers for a given address across multiple contracts."""
    all_transfers = []
    for contract in contracts:
        page = 1
        while True:
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': contract,
                'address': user_address,
                'startblock': 0,
                'endblock': 99999999,
                'page': page,
                'offset': 100,
                'sort': 'asc',
                'apikey': api_key
            }
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if data['status'] != '1' or not data['result']:
                break
                
            all_transfers.extend(data['result'])
            page += 1
    return sorted(all_transfers, key=lambda x: int(x['timeStamp']))

def process_balance_history(transfers, user_address, final_end):
    """Process transfers to create balance history."""
    balance = 0.0
    balance_history = []
    current_ts = None

    for transfer in transfers:
        ts = int(transfer['timeStamp'])
        decimals = int(transfer['tokenDecimal'])
        value = int(transfer['value']) / (10 ** decimals)
        
        if current_ts is not None and ts > current_ts:
            balance_history.append({
                'start': current_ts,
                'end': ts,
                'balance': balance
            })
        
        if transfer['from'].lower() == user_address.lower():
            balance -= value
        elif transfer['to'].lower() == user_address.lower():
            balance += value
        
        current_ts = ts

    if current_ts is not None:
        balance_history.append({
            'start': current_ts,
            'end': final_end,
            'balance': max(balance, 0)
        })
    
    return balance_history

def get_token_price(price_api_url):
    """Fetch token price from Pendle API"""
    try:
        response = requests.get(price_api_url, headers={'accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            return data['prices'].get(price_api_url.split('=')[-1].lower(), 1.0)
        return 1.0  # Fallback price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return 1.0

def calculate_points(user_address):
    """Calculate points and holding days for a given Ethereum address."""
    total_points = 0
    results = []
    current_timestamp = datetime.now(timezone.utc).timestamp()
    
    for token in TOKENS:
        rate_periods = []
        prev_end_date = None
        
        # Convert rate schedule to timestamps
        for schedule in token['points_schedule']:
            end_ts = int(datetime.strptime(schedule['end_date'], "%Y-%m-%d").timestamp())
            rate_periods.append({
                'start': prev_end_date if prev_end_date else 0,
                'end': end_ts,
                'rate': schedule['rate']
            })
            prev_end_date = end_ts + 1  # Prevent overlapping periods

        transfers = get_all_transfers(
            token['base_url'],
            token['contracts'],
            user_address,
            token['api_key']
        )

        if not transfers:
            continue

        # Use current timestamp instead of maturity date for active positions
        final_end = min(rate_periods[-1]['end'], current_timestamp)
        balance_history = process_balance_history(transfers, user_address, final_end)
        
        token_points = 0
        holding_days = 0.0
        current_balance = 0.0
        usd_price = 1.0  # Default for non-LP tokens
        
        # Get USD price for LP tokens
        if 'price_api' in token:
            usd_price = get_token_price(token['price_api'])
        
        for period in balance_history:
            if period['balance'] > 0:
                period_start = max(period['start'], int(transfers[0]['timeStamp']))
                period_end = min(period['end'], current_timestamp)
                period_days = (period_end - period_start) / SECONDS_PER_DAY
                holding_days += max(period_days, 0)  # Prevent negative days
                current_balance = period['balance']
                
                # Calculate USD value for LP tokens
                if 'price_api' in token:
                    usd_value = period['balance'] * usd_price
                else:
                    usd_value = period['balance']
                
                # Points calculation with USD value
                for rate_block in rate_periods:
                    overlap_start = max(period['start'], rate_block['start'])
                    overlap_end = min(period['end'], rate_block['end'])
                    
                    if overlap_start >= overlap_end:
                        continue
                    
                    rate_days = (overlap_end - overlap_start) / SECONDS_PER_DAY
                    token_points += usd_value * rate_days * rate_block['rate']
        
        if 'price_api' in token:
            if token['name'] in ['Base USR LP', 'Ethereum wstUSR LP']:
                results.append({
                    'name': token['name'],
                    'points': round(token_points, 2),
                    'days': round(holding_days, 2),
                    'balance': round(current_balance, 4),
                    'maturity_date': token['maturity_date'],
                    'price': round(usd_price, 4)
                })
            else:
                results.append({
                    'name': token['name'],
                    'points': round(token_points, 2),
                    'days': round(holding_days, 2),
                    'balance': round(current_balance, 4),
                    'maturity_date': token['maturity_date']
                })
        else:
            results.append({
                'name': token['name'],
                'points': round(token_points, 2),
                'days': round(holding_days, 2),
                'balance': round(current_balance, 4),
                'maturity_date': token['maturity_date']
            })
        total_points += token_points
    
    return results, round(total_points, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the main route."""
    if request.method == 'POST':
        user_address = request.form['address']
        
        # Get base results from existing code
        results, base_points = calculate_points(user_address)
        
        # Check boosts and get final points
        boost_results = check_boosts(user_address, base_points)
        
        return render_template('index.html', 
                             results=results, 
                             total_points=boost_results['final_points'],
                             base_points=boost_results['base_points'],
                             bonuses=boost_results['active_boosts'],
                             address=user_address)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
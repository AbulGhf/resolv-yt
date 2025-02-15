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

# Alchemy configuration
ALCHEMY_URL = 'https://base-mainnet.g.alchemy.com/v2/uuLBOZte0sf0z3XRVPPsPKMrfuQ1gqHv'
ALCHEMY_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

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
    {   # Equilibria USR Pool
        'name': 'Equilibria USR Pool',
        'contracts': ['0xE15578523937ed7F08E8F7a1Fa8a021E07025a08'],  # LP token contract
        'points_schedule': [
            {'rate': 60, 'end_date': '2025-04-24'}
        ],
        'maturity_date': '2025-04-24',
        'price_api': 'https://api-v2.pendle.finance/core/v1/8453/assets/prices?addresses=0xE15578523937ed7F08E8F7a1Fa8a021E07025a08',
        'use_alchemy': True,
        'alchemy_targets': [
            '0x2583A2538272f31e9A15dD12A432B8C96Ab4821d',
            '0x920873E5b302A619C54c908aDFB77a1C4256A3B8'
        ]
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
    {   # Base USR LP
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
    {   # Ethereum wstUSR LP
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
            {'rate': 30, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01'
    },
    {   # USR on Base
        'name': 'Base USR',
        'contracts': ['0x35E5dB674D8e93a03d814FA0ADa70731efe8a4b9'],
        'api_key': BASE_API_KEY,
        'base_url': 'https://api.basescan.org/api',
        'points_schedule': [
            {'rate': 30, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01'
    },
    {   # RLP on Ethereum
        'name': 'Ethereum RLP',
        'contracts': ['0x4956b52aE2fF65D74CA2d61207523288e4528f96'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 10, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01'
    },
    {   # RLP on Base
        'name': 'Base RLP',
        'contracts': ['0xC31389794Ffac23331E0D9F611b7953f90AA5fDC'],
        'api_key': BASE_API_KEY,
        'base_url': 'https://api.basescan.org/api',
        'points_schedule': [
            {'rate': 10, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01'
    },
    {   # STUSR
        'name': 'STUSR',
        'contracts': ['0x6c8984bc7DBBeDAf4F6b2FD766f16eBB7d10AAb4'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 5, 'end_date': '2025-12-31'}
        ],
        'maturity_date': '2025-12-31'
    },
    {   # Resolv USDC MORPHO
        'name': 'Resolv USDC MORPHO',
        'contracts': ['0x132E6C9C33A62D7727cd359b1f51e5B566E485Eb'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 5, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01',
        'decimals': 6  # Explicitly specify USDC decimals
    },
        {   # Provide liquidity to USR pool on Curve
        'name': 'USR/USDC Curve',
        'contracts': ['0x3eE841F47947FEFbE510366E4bbb49e145484195'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 55, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01',
    },
            {   # Provide liquidity to RLP pool on Curve
        'name': 'RLP/USDC Curve',
        'contracts': ['0x8e001d4bac0eae1eea348dfc22f9b8bda67dd211'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 45, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01',
    },
            {   # Provide liquidity to USR-RLP pool on Curve
        'name': 'USR-RLP Curve',
        'contracts': ['0xc907ba505c2e1cbc4658c395d4a2c7e6d2c32656'],
        'api_key': ETHERSCAN_API_KEY,
        'base_url': 'https://api.etherscan.io/api',
        'points_schedule': [
            {'rate': 60, 'end_date': '2100-01-01'}
        ],
        'maturity_date': '2100-01-01',
    },
]

SECONDS_PER_DAY = 86400

def get_token_decimals(token):
    """Get token decimals with proper fallback."""
    return token.get('decimals', 18)

def get_alchemy_transfers(user_address, contract_address, target_addresses):
    """Fetch transfers using Alchemy API for multiple target addresses"""
    all_transfers = []
    
    for target_address in target_addresses:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromBlock": "0x0",
                    "toBlock": "latest",
                    "fromAddress": user_address,
                    "toAddress": target_address,
                    "contractAddresses": [contract_address],
                    "category": ["erc20"],
                    "withMetadata": True,
                    "excludeZeroValue": True,
                    "maxCount": "0x3e8"
                }
            ]
        }

        try:
            response = requests.post(ALCHEMY_URL, headers=ALCHEMY_HEADERS, json=payload)
            data = response.json()
            transfers = data.get('result', {}).get('transfers', [])
            for transfer in transfers:
                transfer['target_address'] = target_address
            all_transfers.extend(transfers)
        except Exception as e:
            print(f"Error fetching Alchemy transfers for {target_address}: {e}")
    
    return all_transfers

def format_alchemy_transfers(transfers, decimals=18):
    """Format Alchemy transfers to match the structure of other transfers"""
    formatted_transfers = []
    for t in transfers:
        formatted_transfers.append({
            'timeStamp': int(datetime.fromisoformat(t['metadata']['blockTimestamp']).timestamp()),
            'from': t['from'],
            'to': t['to'],
            'value': int(float(t['value']) * (10 ** decimals)),
            'tokenDecimal': str(decimals),
            'target_address': t['target_address']
        })
    return formatted_transfers

def get_all_transfers(base_url, contracts, user_address, api_key, use_alchemy=False, alchemy_targets=None, decimals=18):
    """Fetch all token transfers for a given address across multiple contracts."""
    if use_alchemy and alchemy_targets:
        all_transfers = []
        for contract in contracts:
            transfers = get_alchemy_transfers(user_address, contract, alchemy_targets)
            formatted_transfers = format_alchemy_transfers(transfers, decimals)
            all_transfers.extend(formatted_transfers)
        return sorted(all_transfers, key=lambda x: int(x['timeStamp']))
    
    # Original API logic for other tokens
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
            try:
                response = requests.get(base_url, params=params)
                data = response.json()
                if data['status'] != '1' or not data['result']:
                    break
                    
                all_transfers.extend(data['result'])
                page += 1
            except Exception as e:
                print(f"Error fetching transfers: {e}")
                break
                
    return sorted(all_transfers, key=lambda x: int(x['timeStamp']))

def process_balance_history(transfers, user_address, final_end):
    """Process transfers to create balance history."""
    balance = 0.0
    balance_history = []
    current_ts = None

    for transfer in transfers:
        ts = int(transfer['timeStamp'])
        # Important: Use the correct decimals from the transfer
        decimals = int(transfer.get('tokenDecimal', '18'))
        value = int(transfer['value']) / (10 ** decimals)
        
        if current_ts is not None and ts > current_ts:
            balance_history.append({
                'start': current_ts,
                'end': ts,
                'balance': balance
            })
        
        # For transfers using Alchemy API (USR Pool)
        if 'target_address' in transfer:
            # Add to balance when user transfers to either target address
            if transfer['from'].lower() == user_address.lower():
                balance += value
        else:
            # Original balance tracking for other tokens
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
        return 1.0
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
            prev_end_date = end_ts + 1

        # Get token decimals
        token_decimals = get_token_decimals(token)

        # Get transfers using appropriate method
        transfers = get_all_transfers(
            token.get('base_url', ''),
            token['contracts'],
            user_address,
            token.get('api_key', ''),
            use_alchemy=token.get('use_alchemy', False),
            alchemy_targets=token.get('alchemy_targets'),
            decimals=token_decimals
        )

        if not transfers:
            continue

        # Add token decimals to transfers if not already present
        for t in transfers:
            if 'tokenDecimal' not in t:
                t['tokenDecimal'] = str(token_decimals)

        final_end = min(rate_periods[-1]['end'], current_timestamp)
        balance_history = process_balance_history(transfers, user_address, final_end)
        
        token_points = 0
        holding_days = 0.0
        current_balance = 0.0
        usd_price = 1.0
        
        if 'price_api' in token:
            usd_price = get_token_price(token['price_api'])
        
        for period in balance_history:
            if period['balance'] > 0:
                period_start = max(period['start'], int(transfers[0]['timeStamp']))
                period_end = min(period['end'], current_timestamp)
                period_days = (period_end - period_start) / SECONDS_PER_DAY
                holding_days += max(period_days, 0)
                current_balance = period['balance']
                
                # Calculate USD value based on token type
                if 'price_api' in token:
                    usd_value = period['balance'] * usd_price
                else:
                    usd_value = period['balance']
                
                for rate_block in rate_periods:
                    overlap_start = max(period['start'], rate_block['start'])
                    overlap_end = min(period['end'], rate_block['end'])
                    
                    if overlap_start >= overlap_end:
                        continue
                    
                    rate_days = (overlap_end - overlap_start) / SECONDS_PER_DAY
                    token_points += usd_value * rate_days * rate_block['rate']
        
        result = {
            'name': token['name'],
            'points': round(token_points, 2),
            'days': round(holding_days, 2),
            'balance': round(current_balance, 4),
            'maturity_date': token['maturity_date']
        }
        
        if 'price_api' in token:
            result['price'] = round(usd_price, 4)
            
        results.append(result)
        total_points += token_points
    
    return results, round(total_points, 2)

def format_timestamp(ts):
    """Convert timestamp to human-readable date."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')

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
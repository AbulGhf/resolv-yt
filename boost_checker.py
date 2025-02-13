# boost_checker.py
import requests

def check_hyperliquid_interaction(address):
    """
    Check if address has interacted with Hyperliquid using Alchemy API
    """
    ALCHEMY_URL = "https://arb-mainnet.g.alchemy.com/v2/uuLBOZte0sf0z3XRVPPsPKMrfuQ1gqHv"
    BRIDGE_ADDRESSES = [
        "0x2df1c51e09aecf9cacb7bc98cb1742757f163df7",
        "0xC67E9Efdb8a66A4B91b1f3731C75F500130373A4"
    ]
    USDC_ADDRESS = "0xaf88d065e77c8cc2239327c5edb3a432268e5831"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    for bridge_address in BRIDGE_ADDRESSES:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromBlock": "0x0",
                    "toBlock": "latest",
                    "fromAddress": address,
                    "toAddress": bridge_address,
                    "contractAddresses": [USDC_ADDRESS],
                    "category": ["erc20"],
                    "withMetadata": True,
                    "excludeZeroValue": True
                }
            ]
        }

        try:
            response = requests.post(ALCHEMY_URL, headers=headers, json=payload)
            data = response.json()
            
            if 'result' in data and data['result']['transfers']:
                transfers = data['result']['transfers']
                if len(transfers) > 0:
                    return True
                    
        except Exception as e:
            continue
    
    return False

def check_dinero_balance(address):
    """
    Check if address holds any Dinero tokens using Alchemy API
    """
    ALCHEMY_URL = "https://eth-mainnet.g.alchemy.com/v2/uuLBOZte0sf0z3XRVPPsPKMrfuQ1gqHv"
    DINERO_TOKEN = "0x04c154b66cb340f3ae24111cc767e0184ed00cc6"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenBalances",
        "params": [
            address,
            [DINERO_TOKEN]
        ]
    }
    
    try:
        response = requests.post(ALCHEMY_URL, headers=headers, json=payload)
        data = response.json()
        
        if 'result' in data and len(data['result']['tokenBalances']) > 0:
            balance_hex = data['result']['tokenBalances'][0]['tokenBalance']
            balance = int(balance_hex, 16)
            return balance > 0
                
        return False
        
    except Exception as e:
        return False

def check_boosts(address, base_points):
    """Check for active boosts and calculate final points."""
    active_boosts = []
    boost_multiplier = 1.0

    # Check Hyperliquid boost
    if check_hyperliquid_interaction(address):
        boost_multiplier += 0.10
        boost_amount = base_points * 0.10
        active_boosts.append({
            'name': 'Hyperliquid Power User',
            'boost': '+10%',
            'amount': round(boost_amount, 2)
        })

    # Check Dinero boost
    if check_dinero_balance(address):
        boost_multiplier += 0.10
        boost_amount = base_points * 0.10
        active_boosts.append({
            'name': 'Dinero Power User',
            'boost': '+10%',
            'amount': round(boost_amount, 2)
        })

    final_points = base_points * boost_multiplier

    return {
        'base_points': round(base_points, 2),
        'final_points': round(final_points, 2),
        'active_boosts': active_boosts
    }
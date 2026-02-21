#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check data structure
"""

import requests
from datetime import datetime

def get_tvl_debug():
    """Debug TVL data structure"""
    defi_llama_base = 'https://api.llama.fi'
    slug = 'aave-v3'
    url = f"{defi_llama_base}/protocol/{slug}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("Raw API response keys:", list(data.keys()))
        print("TVL value:", data.get('tvl', 'Not found'))
        print("TVL type:", type(data.get('tvl', 'Not found')))
        
        if isinstance(data.get('tvl'), list):
            print("TVL is a list! First few items:", data.get('tvl')[:3])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_tvl_debug()
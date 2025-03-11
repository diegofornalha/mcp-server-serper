#!/usr/bin/env python3

"""
Script para testar o endpoint de autocompletar da API Serper.
"""

import http.client
import json

def test_autocomplete():
    conn = http.client.HTTPSConnection('google.serper.dev')
    payload = json.dumps([
        {
            'q': 'agentes de ia',
            'location': 'Brazil',
            'gl': 'br',
            'hl': 'pt-br'
        },
        {
            'q': 'google inc',
            'location': 'Brazil',
            'gl': 'br',
            'hl': 'pt-br'
        },
        {
            'q': 'tesla inc',
            'location': 'Brazil',
            'gl': 'br',
            'hl': 'pt-br'
        }
    ])
    headers = {
        'X-API-KEY': '5b5305befa6a1187c56d7ba06e2971aca87e6a0e',
        'Content-Type': 'application/json'
    }
    
    print("Enviando requisição para o endpoint de autocompletar...")
    conn.request('POST', '/autocomplete', payload, headers)
    
    print("Recebendo resposta...")
    res = conn.getresponse()
    
    print(f"Status: {res.status} {res.reason}")
    data = res.read()
    
    print("Resposta:")
    result = json.loads(data.decode('utf-8'))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    test_autocomplete()
import urllib.request, os, json

url = 'https://gateway.maton.ai/notion/v1/blocks/31470dc2-6079-8129-b043-e5672e2fdf76/children'
api_key = os.environ.get("MATON_API_KEY", "")
req = urllib.request.Request(url, method='GET')
req.add_header('Authorization', f'Bearer {api_key}')
req.add_header('Notion-Version', '2022-06-28')

try:
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
        for block in data.get('results', []):
            if block['type'] == 'paragraph':
                text = "".join([t['plain_text'] for t in block['paragraph']['rich_text']])
                if text.strip() and text.startswith("# 【加入河南"):
                    print(text)
                    break
except Exception as e:
    pass

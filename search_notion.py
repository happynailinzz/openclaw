import urllib.request, os, json

url = 'https://gateway.maton.ai/notion/v1/search'
data = json.dumps({'query': '文章选题草稿箱'}).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')

api_key = os.environ.get("MATON_API_KEY", "")
if not api_key:
    print("Warning: MATON_API_KEY environment variable is not set.")

req.add_header('Authorization', f'Bearer {api_key}')
req.add_header('Content-Type', 'application/json')
req.add_header('Notion-Version', '2022-06-28')

try:
    with urllib.request.urlopen(req) as response:
        print(json.dumps(json.load(response), indent=2))
except urllib.error.URLError as e:
    if hasattr(e, 'read'):
        print(f"Error: {e.code} - {e.read().decode('utf-8')}")
    else:
        print(f"Error: {e}")

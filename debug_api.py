import requests
import sys

print("🔍 Teste detalhado de registro...")

url = "http://localhost:8000/auth/register"
data = {
    "email": "debug@test.com",
    "username": "debug",
    "password": "senha123",
    "full_name": "Debug User"
}

print(f"\n📡 POST {url}")
print(f"📦 Payload: {data}")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📄 Headers: {dict(response.headers)}")
    print(f"🔤 Response Text: {response.text}")
    
    if response.status_code >= 400:
        print(f"\n❌ ERRO {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Não consegui conectar na API. Ela está rodando?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

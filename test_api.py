import requests
import json

print("🧪 Testando API local...")

# Teste 1: Health check
print("\n1️⃣ Testando health check...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Registro
print("\n2️⃣ Testando registro...")
user_data = {
    "email": "teste123@astro.com",
    "username": "teste123",
    "password": "senha789",
    "full_name": "Teste Usuario"
}

try:
    response = requests.post("http://localhost:8000/auth/register", json=user_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Usuário criado: {response.json()}")
    else:
        print(f"   ❌ Erro: {response.text}")
except Exception as e:
    print(f"   ❌ Erro na requisição: {e}")

print("\n✅ Teste finalizado!")

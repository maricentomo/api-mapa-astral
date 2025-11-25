# init_db.py - Script para inicializar o banco de dados

from database import Base, engine
import models

print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")

# Exibir tabelas criadas
print("\n📊 Tabelas criadas:")
for table in Base.metadata.sorted_tables:
    print(f"  - {table.name}")

import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceja_gestao.settings')
django.setup()

def limpar():
    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM professores_professor;")
            cursor.execute("DELETE FROM funcionarios_funcionarioadministrativo;")
            print("Tabelas de professores e funcionarios limpas com sucesso.")
        except Exception as e:
            print(f"Aviso ao limpar tabelas: {e}")

if __name__ == '__main__':
    limpar()

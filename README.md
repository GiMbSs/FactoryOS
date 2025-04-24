# GestorProducao

Sistema completo para gestão de produção, estoque, comercial e financeiro, desenvolvido em Django.

## Funcionalidades
- Cadastro e gerenciamento de clientes e fornecedores
- Controle de vendas e pedidos
- Gestão de contas a pagar e receber
- Controle de estoque de matérias-primas e produtos
- Ordens de produção
- Sistema de logs detalhado para auditoria
- Interface web amigável

## Estrutura do Projeto
```
GestorProducao/
├── comercial/        # App de clientes, fornecedores e vendas
├── estoque/          # App de estoque e matérias-primas
├── financeiro/       # App financeiro (contas a pagar/receber)
├── producao/         # App de produção (ordens, produtos, etc)
├── core/             # Funções utilitárias, log, base
├── templates/        # Templates HTML
├── static/           # Arquivos estáticos
├── manage.py         # Utilitário Django
├── requirements.txt
├── .gitignore
├── README.md
```

## Instalação
1. Clone o repositório
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
5. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```
6. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

Acesse em [http://localhost:8000](http://localhost:8000)

## Observações
- O sistema utiliza SQLite por padrão, mas pode ser adaptado para outros bancos.
- Para produção, configure variáveis de ambiente no arquivo `.env`.
- O sistema de logs registra todas as operações de CRUD.

---
Desenvolvido por GiMbSs

# FControl

Sistema completo para gestão de produção industrial com módulos integrados de estoque, vendas e financeiro, desenvolvido em Django.

![Versão](https://img.shields.io/badge/versão-1.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)

## 📋 Visão Geral

O FControl é um sistema ERP web completo voltado para indústrias de pequeno e médio porte. Foi desenvolvido para otimizar o gerenciamento de processos produtivos, desde o pedido do cliente até a entrega do produto final, integrando todas as áreas do negócio.

### 💼 Módulos Principais

O sistema está dividido em módulos que trabalham de forma integrada:

- **Produção**: Gerencia ordens de produção, produtos acabados e matérias-primas
- **Estoque**: Controle de movimentações, saldos e alertas de níveis mínimos
- **Comercial**: Gestão de clientes, fornecedores e vendas 
- **Financeiro**: Controle de contas a pagar, receber e fluxo de caixa
- **Core**: Funcionalidades gerais, dashboard, logs e autenticação

## ✨ Funcionalidades

### Módulo de Produção
- Cadastro e ficha técnica de produtos
- Gestão de matérias-primas com custos e consumos
- Ordens de produção com status de acompanhamento
- Exportação de ordens para PDF
- **API REST** para integração com outros sistemas
- Configuração de custo da mão de obra

### Módulo de Estoque
- Controle de entrada e saída de matérias-primas
- Gestão de saldos em estoque
- Alertas de estoque abaixo do mínimo
- Histórico de movimentações

### Módulo Comercial
- Cadastro completo de clientes e fornecedores
- Controle de vendas e pedidos
- Histórico de transações

### Módulo Financeiro
- Gestão de contas a pagar e receber
- Controle de fluxo de caixa
- Alertas de contas vencidas ou a vencer

### Recursos Gerais
- Dashboard com indicadores de performance
- Sistema de logs detalhado para auditoria
- APIs REST para integração com outros sistemas
- Interface web responsiva e intuitiva
- Autenticação e controle de acesso

## 🚀 Começando

### Pré-requisitos

- Python 3.11+
- pip (gerenciador de pacotes)
- Git
- Conhecimento básico de linha de comando

### Instalação

1. Clone o repositório
   ```bash
   git clone https://github.com/seu-usuario/FControl.git
   cd FControl
   ```

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

4. Configure o ambiente (opcional):
   - Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias
   - Exemplo:
     ```
     DEBUG=True
     SECRET_KEY=your-secret-key
     DATABASE_URL=sqlite:///db.sqlite3
     ```

5. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

6. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```

7. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

8. Acesse em [http://localhost:8000](http://localhost:8000)

## 🏗️ Estrutura do Projeto

```
FControl/
├── comercial/             # App de gestão comercial
│   ├── views/             # Views organizadas por contexto
│   ├── templates/         # Templates específicos do módulo
│   └── ...
├── estoque/               # App de controle de estoque
├── financeiro/            # App de gestão financeira
├── producao/              # App de gestão da produção
│   ├── views/             # Views separadas por contexto
│   ├── api/               # Endpoints da API REST
│   └── templates/         # Templates específicos do módulo
├── core/                  # Funcionalidades centrais
│   ├── views/             # Dashboard e logs
│   └── ...
├── templates/             # Templates globais
├── static/                # Arquivos estáticos globais
├── media/                 # Arquivos enviados pelos usuários
├── manage.py              # Utilitário Django
├── requirements.txt       # Dependências do projeto
├── docs/                  # Documentação adicional
│   ├── api.md             # Documentação da API REST
│   └── ...
└── README.md              # Este arquivo
```

## 📱 APIs REST

O sistema oferece APIs REST para integração com outros sistemas ou aplicações:

- **API de Produção**:
  - Gerenciamento de produtos, matérias-primas e ordens de produção
  - Consulta de materiais necessários com verificação de estoque

A documentação completa das APIs REST pode ser encontrada em [docs/api.md](docs/api.md).

## ⚙️ Tecnologias Utilizadas

- **Backend**: Django, Django REST framework
- **Frontend**: Bootstrap, jQuery, Chart.js
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (recomendado para produção)
- **Outras bibliotecas**: xhtml2pdf, django-import-export

## 🔧 Configuração para Produção

Para ambientes de produção, recomenda-se:

1. Configurar um servidor web como Nginx ou Apache
2. Utilizar Gunicorn ou uWSGI como servidor WSGI
3. Migrar para um banco de dados robusto como PostgreSQL
4. Configurar backup automático do banco de dados
5. Definir as variáveis de ambiente apropriadas:
   - `DEBUG=False`
   - `ALLOWED_HOSTS=seu-dominio.com`
   - Chaves secretas seguras

## 👩‍💻 Para Desenvolvedores

### Estrutura de Código

O projeto segue uma arquitetura modular, onde cada app Django representa uma área de negócio específica. O código está organizado seguindo princípios de:

- **Separação de Responsabilidades**: Views, models e templates bem definidos
- **DRY (Don't Repeat Yourself)**: Uso de mixins e classes abstratas
- **APIs RESTful**: Endpoints documentados para integração

### Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
2. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
3. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
4. Abra um Pull Request

### Padrões de Código

- PEP 8 para estilo de código Python
- DocStrings para todas as funções e classes
- Testes unitários para funcionalidades críticas

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 📞 Suporte

Para suporte, entre em contato através de:
- Email: [gimbss@gmail.com](mailto:gimbss@gmail.com)
- Issues no GitHub

---

Desenvolvido por GiMbSs © 2023-2025

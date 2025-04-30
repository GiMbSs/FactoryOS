# Documentação da API REST - FControl

## Introdução

O FControl oferece uma API REST completa para integração com outros sistemas, aplicações móveis ou serviços externos. A API segue os princípios RESTful, utilizando JSON como formato padrão para troca de dados e os métodos HTTP padrão para as operações CRUD (Create, Read, Update, Delete).

## Autenticação

Atualmente, a API utiliza a autenticação de sessão do Django. Para acessar os endpoints protegidos, você precisa estar autenticado no sistema.

**Próximas implementações:**
- Autenticação via Token
- Autenticação via JWT (JSON Web Token)

## Endpoints Disponíveis

A API está atualmente organizada dentro do módulo de produção, com os seguintes endpoints principais:

### API de Produção

Base URL: `/api/producao/`

#### 1. Gerenciamento de Produtos

**Endpoint:** `/api/producao/produtos/`

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/producao/produtos/` | Lista todos os produtos cadastrados |
| GET | `/api/producao/produtos/{id}/` | Obtém os detalhes de um produto específico |
| POST | `/api/producao/produtos/` | Cria um novo produto |
| PUT | `/api/producao/produtos/{id}/` | Atualiza um produto existente |
| PATCH | `/api/producao/produtos/{id}/` | Atualiza parcialmente um produto existente |
| DELETE | `/api/producao/produtos/{id}/` | Remove um produto |

**Campos do modelo Produto:**
- `id`: Identificador único do produto (integer)
- `nome`: Nome do produto (string)
- `descricao`: Descrição detalhada do produto (string)
- `tipo`: Tipo do produto (PLASTICO, MADEIRA, TECIDO, MISTO)
- `tipo_produto`: ID do tipo de produto relacionado (integer)
- `tipo_produto_nome`: Nome do tipo de produto (somente leitura)
- `codigo_sku`: Código SKU único do produto (string)
- `custo_producao`: Custo de produção calculado (somente leitura)
- `materias_primas`: Lista de matérias-primas utilizadas na produção (somente leitura)

**Exemplo de resposta:**

```json
{
  "id": 1,
  "nome": "Coador de Café Premium",
  "descricao": "Coador de café em tecido de alta qualidade",
  "tipo": "TECIDO",
  "tipo_produto": 3,
  "tipo_produto_nome": "Coadores",
  "codigo_sku": "COA-TCF-001",
  "custo_producao": 13.75,
  "materias_primas": [
    {
      "materia_prima": {
        "id": 5,
        "nome": "Tecido para filtragem",
        "tipo": "TECIDO_MALHA",
        "unidade_medida": "METRO",
        "custo_unitario": "8.50",
        "saldo": 35.5,
        "custo_total": 301.75
      },
      "quantidade_utilizada": 0.25
    },
    {
      "materia_prima": {
        "id": 8,
        "nome": "Cabo de madeira",
        "tipo": "VARETA_MADEIRA",
        "unidade_medida": "UNIDADE",
        "custo_unitario": "1.20",
        "saldo": 120,
        "custo_total": 144
      },
      "quantidade_utilizada": 1
    }
  ]
}
```

#### 2. Materiais Necessários para Produção

**Endpoint:** `/api/producao/produtos/{produto_id}/materias-primas/`

Esse endpoint especializado retorna as matérias-primas necessárias para produzir determinada quantidade de um produto, além de verificar se há estoque suficiente para a produção.

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/producao/produtos/{produto_id}/materias-primas/?quantidade={quantidade}` | Obtém as matérias-primas necessárias para produzir o produto |

**Parâmetros de URL:**
- `produto_id`: ID do produto (obrigatório)
- `quantidade`: Quantidade a ser produzida (opcional, padrão=1)

**Exemplo de resposta:**

```json
[
  {
    "materia_prima": "Tecido para filtragem",
    "quantidade_total": 0.5,
    "unidade": "METRO",
    "estoque_disponivel": 35.5,
    "suficiente": true
  },
  {
    "materia_prima": "Cabo de madeira",
    "quantidade_total": 2,
    "unidade": "UNIDADE",
    "estoque_disponivel": 120,
    "suficiente": true
  }
]
```

#### 3. Gerenciamento de Matérias-Primas

**Endpoint:** `/api/producao/materias-primas/`

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/producao/materias-primas/` | Lista todas as matérias-primas |
| GET | `/api/producao/materias-primas/{id}/` | Obtém os detalhes de uma matéria-prima |
| POST | `/api/producao/materias-primas/` | Cria uma nova matéria-prima |
| PUT | `/api/producao/materias-primas/{id}/` | Atualiza uma matéria-prima existente |
| PATCH | `/api/producao/materias-primas/{id}/` | Atualiza parcialmente uma matéria-prima |
| DELETE | `/api/producao/materias-primas/{id}/` | Remove uma matéria-prima |

**Campos do modelo MateriaPrima:**
- `id`: Identificador único da matéria-prima
- `nome`: Nome da matéria-prima
- `tipo`: Tipo da matéria-prima
- `unidade_medida`: Unidade de medida (KG, METRO, UNIDADE)
- `custo_unitario`: Custo unitário da matéria-prima
- `saldo`: Saldo atual da matéria-prima em estoque (somente leitura)
- `custo_total`: Custo total baseado no saldo (somente leitura)

**Exemplo de resposta:**

```json
{
  "id": 5,
  "nome": "Tecido para filtragem",
  "tipo": "TECIDO_MALHA",
  "unidade_medida": "METRO",
  "custo_unitario": "8.50",
  "saldo": 35.5,
  "custo_total": 301.75
}
```

#### 4. Gerenciamento de Ordens de Produção

**Endpoint:** `/api/producao/ordens/`

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/producao/ordens/` | Lista todas as ordens de produção |
| GET | `/api/producao/ordens/{id}/` | Obtém os detalhes de uma ordem de produção |
| POST | `/api/producao/ordens/` | Cria uma nova ordem de produção |
| PUT | `/api/producao/ordens/{id}/` | Atualiza uma ordem de produção existente |
| PATCH | `/api/producao/ordens/{id}/` | Atualiza parcialmente uma ordem de produção |
| DELETE | `/api/producao/ordens/{id}/` | Remove uma ordem de produção |

**Campos do modelo OrdemProducao:**
- `id`: Identificador único da ordem de produção
- `produto`: ID do produto a ser produzido
- `produto_nome`: Nome do produto (somente leitura)
- `quantidade`: Quantidade a ser produzida
- `status`: Status da ordem de produção (PLANEJADA, EM_PRODUCAO, FINALIZADA, CANCELADA)
- `status_display`: Representação legível do status (somente leitura)
- `data_inicio`: Data de início da produção
- `data_fim`: Data prevista/real de término da produção

**Exemplo de resposta:**

```json
{
  "id": 12,
  "produto": 1,
  "produto_nome": "Coador de Café Premium",
  "quantidade": 50,
  "status": "EM_PRODUCAO",
  "status_display": "Em Produção",
  "data_inicio": "2025-04-15",
  "data_fim": "2025-04-25"
}
```

## Códigos de Status

A API retorna os seguintes códigos de status HTTP:

- `200 OK`: A solicitação foi bem-sucedida
- `201 Created`: O recurso foi criado com sucesso
- `204 No Content`: A solicitação foi bem-sucedida, mas não há conteúdo para retornar
- `400 Bad Request`: A solicitação contém parâmetros inválidos ou está malformada
- `401 Unauthorized`: Autenticação necessária
- `403 Forbidden`: O usuário não tem permissão para acessar este recurso
- `404 Not Found`: O recurso solicitado não foi encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Futuras Implementações

Estamos trabalhando para expandir a API com os seguintes recursos:

1. **APIs para Módulo Financeiro:**
   - Gestão de contas a pagar e receber
   - Dashboard financeiro com indicadores
   
2. **APIs para Módulo Comercial:**
   - Gestão de clientes e fornecedores
   - Controle de vendas
   
3. **Melhorias de Segurança:**
   - Implementação de autenticação por token
   - Controle de taxa de requisições (rate limiting)
   
4. **Expansão de Funcionalidades:**
   - Relatórios gerenciais via API
   - Integração com sistemas de envio/logística

## Suporte e Contato

Para dúvidas, sugestões ou relato de problemas relacionados à API, entre em contato através de:

- Email: [gimbss@gmail.com](mailto:gimbss@gmail.com)
- Issues no GitHub

---

Última atualização: Abril de 2025
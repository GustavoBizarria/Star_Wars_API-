# Gugas Swapi API

*[Read in English](README.md)*

Protótipo de explorador de dados em linha de comando para a [SWAPI](https://swapi.tech) (Star Wars API), com estética de terminal de dados imperial.

## O que faz

- Navega pelas seis coleções da SWAPI: pessoas, planetas, naves, veículos, espécies e filmes.
- Lista os registros com paginação real (usa `total_pages`/`total_records` da própria API, não pagina em memória).
- Ao abrir um registro, busca o detalhe completo e **resolve relações hipermídia**: quando uma pessoa tem `homeworld`, o programa segue essa URL e mostra o nome do planeta, em vez de exibir só o link.
- Trata erros de rede e HTTP de forma explícita, sem travar o CLI.

## Estrutura do repositório

```
star_wars_api/
│   └── starwars_api/
│       ├── __init__.py            # SwapiClient + CLI logic
│       └── __main__.py            # entrypoint (python -m starwars_api)
├── README.md
└── README.pt-BR.md
```

## Sobre a API

A [SWAPI](https://swapi.tech) é uma REST API pública, sem autenticação, dividida em recursos (`people`, `planets`, `starships`, `vehicles`, `species`, `films`). Dois formatos de resposta:

- **Listagem** — `GET /api/{recurso}?page=1&limit=10` devolve um resumo (`uid`, `name`, `url`) por item, mais metadados de paginação.
- **Detalhe** — `GET /api/{recurso}/{uid}` devolve o objeto completo dentro de `result.properties`.

Campos relacionados (como `homeworld` em uma pessoa) não trazem o valor embutido — trazem uma URL para outro recurso, que precisa ser buscada separadamente. O CLI implementa essa resolução como exemplo.

## Stack

Apenas biblioteca padrão do Python (`urllib`, `json`) — nenhuma dependência externa.

### Requisitos

- Python 3.8+

### Uso

```bash
cd cli
python3 -m starwars_api
```

Navegue pelo menu numérico, use `n`/`p` para paginar, digite o número do registro para abrir o detalhe, `v` para voltar e `q` para sair.

## Arquitetura

O pacote é dividido em dois arquivos com responsabilidades distintas:

| Arquivo | Responsabilidade |
|---|---|
| `starwars_api/__init__.py` | Tudo: `SwapiClient` (camada de acesso HTTP + JSON), funções de apresentação (`show_list`, `show_detail`, `format_value`) e o loop de controle (`main`, `browse_category`) |
| `starwars_api/__main__.py` | Entrypoint do pacote — permite rodar `python -m holonet_terminal`; importa `main` de `__init__.py` e chama |

Dentro de `__init__.py`, as três responsabilidades continuam separadas mesmo vivendo no mesmo arquivo:

1. **Acesso a dados** — `SwapiClient` e `SwapiError` isolam todo o tratamento de HTTP/JSON. Nada mais no programa toca `urllib` diretamente.
2. **Apresentação** — `format_value`, `print_header`, `boot_sequence`, `show_list`, `show_detail` transformam dados já buscados em saída de terminal, sem saber nada sobre rede.
3. **Controle** — `browse_category` e `main` leem a entrada do usuário (escolhas de menu, navegação de página, seleção de registro) e decidem quais funções chamar.

A execução é síncrona e bloqueante: cada requisição espera a resposta antes de continuar, o que é adequado para um protótipo de linha de comando. Uma versão de produção com muitas requisições poderia migrar para `asyncio` + `aiohttp` para paralelizar as chamadas.

## Possíveis próximos passos

- Busca por nome usando o parâmetro `?name=` da própria API, em vez de filtro local.
- Cache em disco para evitar refazer a mesma requisição.
- Modo não-interativo via `argparse` (ex.: `holonet_terminal people 4`).
- Testes automatizados com mocks das respostas da SWAPI.

## Créditos

Dados fornecidos por [SWAPI](https://swapi.tech). Star Wars e todos os nomes, personagens e elementos relacionados são marcas registradas da Lucasfilm Ltd. Este projeto é um protótipo não-oficial, sem qualquer afiliação.

## Licença

MIT — sinta-se livre para usar, modificar e distribuir.
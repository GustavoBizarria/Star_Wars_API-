# Gugas Swapi API

*[Ler em português](README.pt-BR.md)*

A command-line data-exploration prototype for the [SWAPI](https://swapi.tech) (Star Wars API), styled like an Imperial data terminal.

## What it does

- Browses all six SWAPI collections: people, planets, starships, vehicles, species, and films.
- Lists records with real pagination (uses the API's own `total_pages`/`total_records`, not in-memory paging).
- When you open a record, it fetches the full detail and **resolves hypermedia relations**: when a person has a `homeworld`, the program follows that URL and shows the planet's name instead of just the link.
- Handles network and HTTP errors explicitly, without crashing the CLI.

## Repository structure

```
star_wars_api/
│   └── starwars_api/
│       ├── __init__.py            # SwapiClient + CLI logic
│       └── __main__.py            # entrypoint (python -m starwars_api)
├── README.md
└── README.pt-BR.md
```

## About the API

[SWAPI](https://swapi.tech) is a public REST API, no authentication required, split into resources (`people`, `planets`, `starships`, `vehicles`, `species`, `films`). Two response shapes:

- **List** — `GET /api/{resource}?page=1&limit=10` returns a summary (`uid`, `name`, `url`) per item, plus pagination metadata.
- **Detail** — `GET /api/{resource}/{uid}` returns the full object inside `result.properties`.

Related fields (like `homeworld` on a person) don't carry the embedded value — they carry a URL to another resource, which has to be fetched separately. The CLI implements that resolution as an example.

## Stack

Python standard library only (`urllib`, `json`) — no external dependencies.

### Requirements

- Python 3.8+

### Usage

```bash
cd cli
python3 -m starwars_api
```

Navigate the numbered menu, use `n`/`p` to page through results, type a record's number to open its detail view, `v` to go back, and `q` to quit.

## Architecture

The package is split into two files with distinct responsibilities:

| File | Responsibility |
|---|---|
| `starwars_api/__init__.py` | Everything: `SwapiClient` (HTTP + JSON access layer), presentation helpers (`show_list`, `show_detail`, `format_value`), and the control loop (`main`, `browse_category`) |
| `starwars_api/__main__.py` | Package entrypoint — lets you run `python -m starwars_api`; imports `main` from `__init__.py` and calls it |

Inside `__init__.py`, the three concerns are still kept apart even though they live in one file:

1. **Data access** — `SwapiClient` and `SwapiError` isolate all HTTP/JSON handling. Nothing else in the program touches `urllib` directly.
2. **Presentation** — `format_value`, `print_header`, `boot_sequence`, `show_list`, `show_detail` turn already-fetched data into terminal output, with no knowledge of networking.
3. **Control** — `browse_category` and `main` read user input (menu choices, page navigation, record selection) and decide which functions to call.

Execution is synchronous and blocking: each request waits for a response before continuing, which is fine for a command-line prototype. A production version handling many requests could move to `asyncio` + `aiohttp` to parallelize calls.

## Possible next steps

- Name search using the API's own `?name=` parameter instead of local filtering.
- Disk cache to avoid repeating the same request.
- Non-interactive CLI mode via `argparse` (e.g. `holonet_terminal people 4`).
- Automated tests with mocked SWAPI responses.

## Credits

Data provided by [SWAPI](https://swapi.tech). Star Wars and all related names, characters, and elements are trademarks of Lucasfilm Ltd. This project is an unofficial prototype with no affiliation.

## License

MIT — feel free to use, modify, and distribute.

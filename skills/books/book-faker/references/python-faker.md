# Python Faker (joke2k/Faker)

Source: <https://faker.readthedocs.io/en/master/> (v40.38.0 at capture).
Use when a Python project needs fake data; the JS chapters above do NOT apply.

## Install & basics

- `pip install Faker` (Python >= 3.8; v4.0 dropped Python 2; the package was
  once named `fake-factory` — ensure nothing still depends on that).

```python
from faker import Faker
fake = Faker()
fake.name(); fake.address(); fake.text()
```

- Each call returns a new random value (generator forwards to
  `Generator.format(method_name)`).

## Providers

- Generator properties ("fakes") are packaged in providers; extend with
  `fake.add_provider(...)`:

```python
from faker.providers import internet
fake.add_provider(internet)
fake.ipv4_private()
```

- Bundled + community provider lists: faker.readthedocs.io/en/stable/
  providers.html and communityproviders.html.

## Localization

- `Faker('it_IT')` for one locale; fallback default is `en_US`.
- Multiple locales: `Faker(['it_IT', 'en_US', 'ja_JP'])` — random per call.
- Locale availability: under the `providers` package in source.

## Determinism & performance

- `Faker(seed=...)` / `fake.seed_instance(...)` for reproducible sequences.
- Constructor arg `use_weighting=True` (default) makes value frequency match
  real-world frequency (e.g. 'Gary' more common than 'Lorimer');
  `use_weighting=False` = uniform pick, much faster.

## CLI

```text
faker [-h] [--version] [-o FILENAME] [-l LOCALE] [-r REPEAT] [-s SEP]
      [-i package.containing.custom_provider] [fake] [fake argument ...]
```

- Examples: `faker address`, `faker name -r 5`; `faker profile` accepts a
  comma-separated list of field names as its first argument.
- In dev checkouts: `python -m faker` instead of the `faker` script.

## pytest plugin

- Ships a `faker` fixture: declare `def test_x(faker):` and use it directly;
  docs page: faker.readthedocs.io (pytest fixture docs).

## JS ↔ Python concept map

| Concept | JS | Python |
| --- | --- | --- |
| Instance | `faker` / `new Faker({locale})` | `Faker(locale)` |
| Seed | `faker.seed(n)` | `fake.seed_instance(n)` |
| Locale | `fakerDE` export | `Faker('de_DE')` |
| Providers | modules on faker | `add_provider(...)` |
| CLI | — | `faker` command |
| Tests | manual seeding | `faker` pytest fixture |

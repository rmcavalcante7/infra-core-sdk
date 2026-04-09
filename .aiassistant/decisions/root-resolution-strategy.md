# Root Resolution Strategy

## Context

O SDK apresentou problema real quando instalado e executado fora do repositorio original.

Depender apenas de `cwd` era insuficiente para o projeto consumidor.

## Decision

A estrategia de root resolution deve seguir esta ordem:

1. `start_path` configurado
2. `cwd`
3. fallback pelo chamador apenas quando o SDK estiver instalado em `site-packages` ou `dist-packages`

## Consequences

- `RootConfig` deve continuar suportando `start_path`
- o fallback do chamador nao deve ser usado indiscriminadamente em desenvolvimento local
- alteracoes futuras nesse fluxo exigem validacao em ambiente instalado, nao apenas em `PYTHONPATH=src`

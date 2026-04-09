# PyPI Release Strategy

## Context

O projeto precisa de um processo de release reproduzivel, auditavel e menos dependente de operacao manual local.

## Decision

O fluxo padrao de publicacao e:

1. validar localmente
2. commitar no `main`
3. criar tag de release
4. enviar branch e tag
5. GitHub Actions builda, valida e publica no PyPI

Publicacao manual com `twine upload` nao e o fluxo preferencial.

## Consequences

- o segredo `PYPI_API_TOKEN` deve ficar no GitHub Actions
- o workflow `.github/workflows/publish.yml` passa a ser parte critica do processo de release
- releases futuras devem seguir o runbook de publicacao do projeto

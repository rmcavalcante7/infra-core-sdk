# Public API Surface

## Context

O SDK sera consumido por outros projetos Python.

Se a API publica nao estiver clara, o consumidor passa a depender de caminhos internos e a superficie publica fica instavel.

## Decision

A API publica principal deve ser exposta no topo do pacote e em subpacotes selecionados.

Topo de `infra_core`:

- `CredentialsLoader`
- `CredentialsService`
- `CredentialsSetupService`
- `FernetEncryption`
- `PathConfig`
- `PathManager`
- `RootConfig`
- `RootConfigProvider`
- `RootResolver`

Subpacotes relevantes:

- `infra_core.core.root`
- `infra_core.exceptions`
- `infra_core.credentials.exceptions`

## Consequences

- novos contratos publicos devem ser adicionados conscientemente aos `__init__.py`
- evitar exigir imports internos longos quando existir caminho publico razoavel
- mudancas na API publica devem ser tratadas como mudancas de produto, nao apenas detalhe interno

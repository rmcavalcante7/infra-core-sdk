# Release PyPI

## Objetivo

Publicar uma nova versao de `infra-core-sdk` no PyPI a partir de uma tag git.

Este projeto deve usar o fluxo:

1. validar localmente
2. commitar no `main`
3. criar tag `vX.Y.Z` ou `vX.Y.Z.postN`
4. enviar branch e tag
5. GitHub Actions builda, valida e publica no PyPI

Publicacao manual com `twine upload` nao e o fluxo preferencial deste projeto.

---

## Pre-requisitos

- acesso de push ao repositorio
- segredo `PYPI_API_TOKEN` configurado em `GitHub -> Settings -> Secrets and variables -> Actions`
- workflow [`publish.yml`](/C:/Users/rafael.m.cavalcante/PycharmProjects/infra-core-sdk/.github/workflows/publish.yml) presente e ativo

---

## Validacao local obrigatoria

Executar na raiz do projeto:

```bash
python -m black .
python -m mypy src
python -m pytest
python -m build
python -m twine check dist/*
```

Se qualquer etapa falhar, nao criar tag.

---

## Atualizacao de versao

Este projeto usa `setuptools_scm`.

A versao publicada e derivada da tag git.

Exemplos validos:

```bash
git tag v0.2.2
git tag v0.2.2.post0
git tag v0.2.2.post1
```

Regra importante:

- README e qualquer documentacao de release devem refletir a nova versao antes do commit final

---

## Fluxo de release

### 1. Garantir tree limpo

```bash
git status --short
```

O resultado deve estar vazio antes da tag.

### 2. Enviar branch principal

```bash
git push origin main
```

### 3. Criar a tag da release

Exemplo:

```bash
git tag v0.2.1.post2
```

### 4. Enviar a tag

```bash
git push origin v0.2.1.post2
```

---

## O que o GitHub Actions deve fazer

Ao receber a tag `v*`, o workflow de publicacao deve:

1. fazer checkout do codigo
2. configurar Python
3. instalar dependencias de build
4. gerar wheel e sdist
5. validar com `twine check`
6. publicar no PyPI com `PYPI_API_TOKEN`

---

## Validacao pos-publicacao

Depois que o workflow concluir:

1. conferir a pagina da nova versao no PyPI
2. instalar a versao publicada em ambiente limpo
3. validar imports publicos
4. validar um script consumidor minimo

Comandos sugeridos:

```bash
pip install infra-core-sdk==<nova_versao>
```

Depois testar:

```python
from infra_core import (
    CredentialsLoader,
    CredentialsSetupService,
    FernetEncryption,
    PathConfig,
    PathManager,
    RootConfig,
    RootConfigProvider,
    RootResolver,
)
```

---

## Critério de encerramento

Uma release so deve ser considerada concluida quando:

- a tag estiver no remoto
- o workflow de publish estiver verde
- a versao estiver visivel no PyPI
- a instalacao da versao publicada tiver sido testada

---

## Observacoes

- usar `postN` quando a base da versao ja existe e a release precisa de ajuste incremental
- nao criar tag antes de validar `black`, `mypy`, `pytest`, `build` e `twine check`
- nao usar `twine upload` manual como caminho padrao enquanto o fluxo por git tag estiver disponivel

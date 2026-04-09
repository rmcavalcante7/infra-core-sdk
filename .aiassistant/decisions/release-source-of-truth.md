# Release Source Of Truth

## Context

O projeto precisa publicar versoes coerentes no PyPI sem depender de alteracao manual de string de versao no codigo.

O repositório ja usa `setuptools_scm`.

## Decision

A fonte de verdade da versao publicada e a tag git.

Exemplos validos:

- `v0.2.2`
- `v0.2.2.post0`
- `v0.2.2.post1`

## Consequences

- a versao nao deve ser mantida manualmente em modulos Python
- a release deve sempre ser disparada a partir de tag
- README e documentacao podem mencionar a versao atual, mas a versao de build vem da tag

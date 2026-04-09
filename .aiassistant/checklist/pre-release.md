# Pre-release Checklist

Use este checklist antes de criar uma nova tag de release.

## Git

- [ ] `git status --short` esta limpo
- [ ] branch correta esta selecionada
- [ ] mudancas da release foram commitadas

## Qualidade

- [ ] `python -m black .` executado
- [ ] `python -m mypy src` passou
- [ ] `python -m pytest` passou

## Build

- [ ] `python -m build` passou
- [ ] `python -m twine check dist/*` passou
- [ ] artefatos esperados existem em `dist/`

## Documentacao

- [ ] `README.md` reflete a versao que sera publicada
- [ ] exemplos mostrados no README continuam coerentes com a API publica

## Release

- [ ] nome da nova tag foi definido corretamente
- [ ] workflow `.github/workflows/publish.yml` esta presente
- [ ] segredo `PYPI_API_TOKEN` ja existe no GitHub Actions

## Publicacao

- [ ] `git push origin main` esta pronto para execucao
- [ ] `git tag <nova_versao>` esta pronto para execucao
- [ ] `git push origin <nova_versao>` esta pronto para execucao

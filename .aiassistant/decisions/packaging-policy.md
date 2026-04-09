# Packaging Policy

## Context

O projeto chegou a gerar `sdist` com arquivos locais e artefatos que nao agregavam valor ao consumidor do SDK.

Isso aumenta ruído e risco operacional na distribuicao.

## Decision

Os artefatos publicados devem conter apenas o necessario para consumo e distribuicao do SDK.

Devem entrar:

- codigo fonte do pacote
- README
- LICENSE
- arquivos minimos de empacotamento

Nao devem entrar por padrao:

- segredos locais
- testes
- docs auxiliares locais
- arquivos de IDE
- zips e artefatos temporarios

## Consequences

- `MANIFEST.in` passa a ser parte importante da manutencao do projeto
- qualquer mudanca relevante em empacotamento deve ser validada com `python -m build` e inspeção do artefato
- exemplos incluidos no pacote devem ser intencionais, nao acidentais

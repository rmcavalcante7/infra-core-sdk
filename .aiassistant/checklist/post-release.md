# Post-release Checklist

Use este checklist logo apos o push da tag e a execucao do workflow de publicacao.

## GitHub

- [ ] a tag existe no remoto
- [ ] o workflow de publish iniciou
- [ ] o workflow de publish terminou com sucesso

## PyPI

- [ ] a nova versao aparece no PyPI
- [ ] a pagina da versao publicada esta acessivel
- [ ] o README renderizado no PyPI ficou aceitavel

## Instalacao real

- [ ] `pip install infra-core-sdk==<versao>` funciona em ambiente limpo
- [ ] imports publicos principais funcionam apos instalacao
- [ ] um script consumidor simples executa sem erro

## Funcionalidade minima

- [ ] `RootConfig` e `RootResolver` funcionam no projeto consumidor
- [ ] `PathConfig` e `PathManager` funcionam no projeto consumidor
- [ ] `CredentialsSetupService(FernetEncryption)` funciona
- [ ] `CredentialsLoader.load(...)` funciona

## Encerramento

- [ ] release considerada concluida
- [ ] eventuais problemas encontrados foram registrados para a proxima versao

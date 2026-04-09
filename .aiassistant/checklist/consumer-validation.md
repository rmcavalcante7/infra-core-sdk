# Consumer Validation Checklist

Use este checklist para validar o SDK do ponto de vista de um projeto consumidor.

## Ambiente

- [ ] criar ambiente virtual limpo
- [ ] instalar a versao desejada do pacote

## Instalacao

- [ ] `pip install infra-core-sdk==<versao>` passou
- [ ] dependencia `cryptography` foi instalada corretamente

## Imports

- [ ] `from infra_core import CredentialsLoader`
- [ ] `from infra_core import CredentialsSetupService`
- [ ] `from infra_core import FernetEncryption`
- [ ] `from infra_core import PathConfig`
- [ ] `from infra_core import PathManager`
- [ ] `from infra_core import RootConfig`
- [ ] `from infra_core import RootConfigProvider`
- [ ] `from infra_core import RootResolver`

## Root resolution

- [ ] o consumidor consegue configurar `RootConfig`
- [ ] o root e resolvido corretamente com `cwd` externo
- [ ] o uso de `start_path` funciona quando necessario

## Paths

- [ ] `PathConfigProvider.set(...)` funciona
- [ ] `PathManager().getPath(...)` funciona
- [ ] `PathManager().ensurePathExists(...)` funciona

## Credentials

- [ ] `CredentialsSetupService(FernetEncryption)` cria chave e arquivo
- [ ] `CredentialsLoader.load(...)` retorna objeto tipado
- [ ] o arquivo de credenciais e criado no path esperado

## Resultado final

- [ ] o fluxo basico de uso do SDK no consumidor foi validado

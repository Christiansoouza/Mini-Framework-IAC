
# 🚀 Projeto AWS Infraestrutura Automatizada

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Automatize a criação e gestão de recursos AWS (ECS, ECR, RDS, VPC, Security Groups) com Python e CloudFormation. Ideal para DevOps, desenvolvedores e equipes que buscam agilidade e segurança na infraestrutura.

## Funcionalidades

- Provisionamento automático de:
  - ECS (Elastic Container Service)
  - ECR (Elastic Container Registry)
  - RDS (Relational Database Service)
  - VPC (Virtual Private Cloud)
  - Security Groups
- Templates CloudFormation prontos
- Scripts para backup e restore
- Gerenciamento de ambientes (dev/prod)
- Leitura e manipulação de arquivos JSON/YAML

## Estrutura do Projeto

```
├── main.py
├── constructores/
├── models/
├── scripts/
├── templates/
├── utils/
├── variables/
├── enviroment/
├── docs/
```

## Como Utilizar: Passo a Passo

### 1. Crie o template YAML
No diretório `templates/`, crie um arquivo YAML (exemplo: `meu-recurso-stack.yaml`) com a estrutura do recurso AWS desejado.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Template para criar recurso X
Resources:
	MeuRecurso:
		Type: AWS::AlgumServico
		Properties:
			Nome: !Ref NomeVariavel
```

### 2. Defina as variáveis
No diretório `variables/variables.py`, crie as variáveis que o template irá utilizar:

```python
NOME_VARIAVEL = {"chave":"valor"}
# ... outras variáveis ...
```

### 3. Crie um constructor herdando de base_constructor
No diretório `constructores/`, crie um arquivo (exemplo: `meu_constructor.py`) e implemente:

```python
from .base_constructor import BaseConstructor

class MeuConstructor(BaseConstructor):
		def __init__(self, variables):
				super().__init__(variables)
				# ... lógica específica ...

		def build(self):
				# ... chamada para criar recurso ...
```

### 4. Executor: modos de uso (deploy, plan, destroy)
O projeto possui uma função `executor` flexível para executar stacks individualmente ou em lote, com as ações `deploy`, `plan` e `destroy`.

#### Como usar:

- Para executar uma stack na main:

```python
executor(variables, constructor, PROFILE, REGION, action="deploy")
```

- Para planejar na main:

```python
executor(variables, constructor, PROFILE, REGION, action="plan")
```

- Para destruir na main:

```python
executor(variables, constructor, PROFILE, REGION, action="destroy")
```

- Para executar várias stacks:

```python
for vars, key in stacks:
	executor(vars, key, PROFILE, REGION, action="deploy")
```

---
Com isso, você pode controlar facilmente o ciclo de vida da sua infraestrutura AWS, seja individualmente ou em lote.
Se quiser construir toda a infraestrutura de uma vez e planejar quais stacks vão subir, utilize a função `run_all()`:

```python
def run_all():
	stacks = [
		(ecs_variables, "ecs"),
		(vpc_variables, "vpc"),
		(rds_variables, "rds"),
		(sgs_alb_variables, "sgs-alb"),
		(sgs_ecs_variables, "sgs-ecs"),
		(sgs_rds_variables, "sgs-rds"),
		(ecr_variables, "ecr")
	]

	for vars, key in stacks:
		executor(vars, key, PROFILE, REGION, action="deploy")

# Basta chamar run_all() na main para subir tudo:
if __name__ == "__main__":
	run_all()
```

Assim, você pode planejar e executar toda a infraestrutura de forma automatizada e modular.
No `main.py`, instancie o constructor e execute:

```python
from constructores.meu_constructor import MeuConstructor
from variables.variables import NOME_VARIAVEL

if __name__ == "__main__":
		executor = MeuConstructor({"NomeVariavel": NOME_VARIAVEL})
		executor.build()
```

---
Esses passos garantem modularidade e facilidade para criar novos recursos AWS.

## Tecnologias Utilizadas

- Python 3.10+
- AWS CloudFormation
- Boto3
- Git

## Contato

Christian Silva — [LinkedIn](https://www.linkedin.com/in/christiansoouza/)

---
<p align="center">Feito com 💙 para automação AWS</p>

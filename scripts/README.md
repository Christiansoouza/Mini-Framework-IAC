# 📜 Scripts de Automação AWS

Documentação dos scripts utilitários para operações e automações no projeto.

## Lista de Scripts

### deploy_restore_ec2_from_database.py
- **Descrição:** Sobe uma instância EC2, conecta ao banco de dados e restaura o backup SQL diretamente na máquina do banco.
- **Parâmetros:**
  - Configuração de ambiente e credenciais AWS.
  - Caminho do backup SQL.
- **Exemplo de uso:**
  ```bash
  python scripts/deploy_restore_ec2_from_database.py
  ```
- **Observações:**
  - Certifique-se de que as permissões AWS estejam corretas.
  - O script provisiona a EC2, transfere o backup e executa o restore no banco.
  - Atua como um Bastion Host temporário para operações seguras e controladas.
  - Pode ser adaptado para diferentes bancos e cenários de restore.

### send_image_to_ecr.py
- **Descrição:** Envia uma imagem Docker para o Amazon ECR.
- **Parâmetros:**
  - Nome do repositório ECR.
  - Caminho da imagem Docker.
- **Exemplo de uso:**
  ```bash
  python scripts/send_image_to_ecr.py --repo my-repo --image ./my-image:latest
  ```
- **Observações:**
  - Requer autenticação prévia no ECR.

---

## Boas Práticas
- Sempre documente parâmetros e exemplos de uso.
- Scripts devem ser claros e modularizados.
- Utilize logs para facilitar troubleshooting.

## Contribuição
Sugestões e melhorias são bem-vindas!

---
<p align="center">Scripts para automação e produtividade</p>

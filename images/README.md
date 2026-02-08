# Exemplo de estrutura para múltimas imagens Docker
# Cada subpasta representa um serviço/imagem diferente

images/
├── app1/
│   ├── Dockerfile
│   └── src/  # Código fonte do app1
├── app2/
│   ├── Dockerfile
│   └── src/  # Código fonte do app2
└── base/
    └── Dockerfile  # Imagem base customizada (opcional)

# Recomendações:
# - Separe cada serviço/módulo em uma subpasta.
# - Cada subpasta deve conter seu próprio Dockerfile e contexto.
# - Use nomes claros para as pastas (ex: web, worker, db, etc).
# - Mantenha dependências e scripts específicos de cada imagem dentro da respectiva pasta.
# - Se precisar de uma imagem base customizada, crie uma pasta base/.

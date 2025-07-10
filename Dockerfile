# Use a imagem oficial do Python como base
FROM python:3.12-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Define o comando padrão para executar a aplicação
# Isso permite que o usuário execute o contêiner e passe argumentos para o main.py
ENTRYPOINT ["python", "main.py"]

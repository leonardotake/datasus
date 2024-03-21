# Use a imagem oficial do Python
FROM python:3.8-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Atualize o sistema e instale as dependências
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Instale as dependências Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código-fonte para o contêiner
COPY . .

# Exponha a porta para o Streamlit
EXPOSE 8501

# Comando padrão para executar o Streamlit
CMD ["streamlit", "run", "app.py"]

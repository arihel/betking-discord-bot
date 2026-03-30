# 1. Pega uma versão oficial e leve do Python
FROM python:3.11-slim

# 2. Define a pasta de trabalho lá dentro do container
WORKDIR /app

# 3. Copia a lista de compras e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia todo o resto do seu código para dentro do container
COPY . .

# 5. O comando que o container vai dar para ligar o bot
CMD ["python", "main.py"]
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Expose ports
EXPOSE 8000 8501

# Start script
RUN chmod +x start.sh

CMD ["./start.sh"]

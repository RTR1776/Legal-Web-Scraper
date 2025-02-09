FROM python:3.10-slim

# Avoid writing .pyc files and enable unbuffered logging.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies.
RUN apt-get update && apt-get install -y build-essential gcc

# Copy and install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code.
COPY . .

EXPOSE 8000

# Run the FastAPI app using Uvicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
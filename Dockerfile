FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if available
COPY requirements.txt* /app/

# Install python dependencies. We explicitly install the stack in case requirements.txt is missing.
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi && \
    pip install --no-cache-dir fastapi uvicorn pydantic requests rich sentence-transformers torch

# Copy the rest of the application
COPY . /app/

# Expose the FastAPI server port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "essasearch.server:app", "--host", "0.0.0.0", "--port", "8000"]

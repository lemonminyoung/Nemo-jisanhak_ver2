# Use official Playwright image with Python
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only)
RUN playwright install chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start command (Version 2 - Gemini Only)
CMD ["uvicorn", "backend_gemini_only:app", "--host", "0.0.0.0", "--port", "8000"]

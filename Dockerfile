# # Use an official Python image
# FROM python:3.9

# # Install dependencies
# RUN apt-get update && apt-get install -y firefox-esr \
#     && pip install selenium streamlit

# # Copy the project files
# COPY . /app
# WORKDIR /app

# # Run Streamlit when the container starts
# CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.enableCORS=false"]

FROM python:3.11-slim

WORKDIR /app

# Install Chromium, ChromeDriver and other dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy application code and install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expose port for Streamlit
EXPOSE 8501

# Start the application
# CMD ["sh", "-c", "streamlit run app.py"]
CMD ["sh", "-c", "streamlit run --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false --server.address=0.0.0.0 app.py"]
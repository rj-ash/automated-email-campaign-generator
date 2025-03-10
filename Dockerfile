FROM selenium/standalone-chromium

WORKDIR /app

# Install Python virtual environment tools
RUN sudo apt-get update && sudo apt-get install -y python3-venv && sudo rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create a virtual environment and install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Set environment variables
# ENV PATH="/app/venv/bin:$PATH"
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expose port for Streamlit
EXPOSE 8501


# Start the application
CMD ["python3", "-m", "streamlit", "run", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.address=0.0.0.0", "app.py"]
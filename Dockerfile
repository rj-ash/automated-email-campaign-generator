# Use an official Python image
FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y firefox-esr \
    && pip install selenium streamlit

# Copy the project files
COPY . /app
WORKDIR /app

# Run Streamlit when the container starts
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.enableCORS=false"]
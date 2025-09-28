# Use a minimal Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only your app files
COPY main.py chain.py requirements.txt ./

# Copy your local pip cache (adjust the path if needed)
COPY "C:/Users/Krish/AppData/Local/pip/Cache" /root/.cache/pip

# Install requirements using only cached packages
RUN pip install --no-index --find-links=/root/.cache/pip -r requirements.txt

# Expose the port your FastAPI app will run on
EXPOSE 8080

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

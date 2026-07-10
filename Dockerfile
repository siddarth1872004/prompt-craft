# Step 1: Use an official light Python image as the starting base
FROM python:3.11-slim

# Step 2: Set the folder inside the Docker container where our files will go
WORKDIR /app

# Step 3: Copy the dependency list and install them inside Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn

# Step 4: Copy the rest of our project files into the container
COPY . .

# Step 5: Inform Docker that the application will listen on port 8000
EXPOSE 8000

# Step 6: Start the Streamlit app when the container runs
CMD ["streamlit", "run", "app.py", "--server.port", "8000", "--server.address", "0.0.0.0"]

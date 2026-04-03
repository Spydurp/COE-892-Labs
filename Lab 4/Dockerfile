# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file (create one if it doesn't exist)
# Assuming you have a requirements.txt in Lab 4/ or create it with: fastapi, uvicorn[standard], pydantic
COPY "requirements.txt" ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Lab 4 directory contents into the container
COPY "." "./Lab4"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "Lab4/server.py"]
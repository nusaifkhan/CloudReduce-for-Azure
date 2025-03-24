# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .
# Copy the Python dependencies file.

# Copy the Python script to the working directory
COPY script.py .
# Copy the main Python script for the application.

# Copy the .env file to the working directory
COPY .env .
# Copy the environment file containing credentials to the container.

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Install the required Python libraries listed in requirements.txt.

# Set the default command to run the script when the container starts
CMD ["python", "script.py"]
# Run the Python script as the main application.

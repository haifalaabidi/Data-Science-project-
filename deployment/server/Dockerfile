# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /server

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Copy the model directory to the working directory
COPY model /server/model

COPY app.py .


# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run your Flask application
CMD [ "python", "app.py" ]

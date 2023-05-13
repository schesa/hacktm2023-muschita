# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the working directory
COPY src/ /app/src
COPY requirements.txt /app

# Copy the .aws/credentials file to the container
COPY ./credentials/credentials /root/.aws/credentials
RUN chmod 600 /root/.aws/credentials

# Install project dependencies
RUN pip3.9 install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5002

# Run the application when the container starts
CMD ["python3.9", "src/app.py"]

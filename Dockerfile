# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /clapp

# Copy the current directory contents into the container at /clapp
COPY . /clapp

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]

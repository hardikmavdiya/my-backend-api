   
   
   
   # Use an official Python runtime as a parent image
    # We use a slim-buster image for a smaller footprint
    FROM python:3.11-slim-bookworm

    # Set the working directory in the container
    WORKDIR /app

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install any needed packages specified in requirements.txt
    # We use --no-cache-dir to save space
    # We also install gunicorn, a production-ready WSGI server for Flask
    RUN pip install --no-cache-dir -r requirements.txt gunicorn

    # Copy the rest of the application code into the container
    COPY . .

    # Expose port 8080. Cloud Run expects containers to listen on 8080.
    EXPOSE 8080

    # Define environment variable for Flask (optional, but good practice)
    ENV FLASK_APP=backend_app.py
    ENV FLASK_ENV=production 
    

    # Run the application using Gunicorn.
    # We bind to 0.0.0.0:8080 as required by Cloud Run.
    # The 'backend_app:app' refers to 'app' object in 'backend_app.py'
    CMD ["gunicorn", "--bind", "0.0.0.0:8080", "backend_app:app"]
    



    
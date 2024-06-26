# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

# Install Firefox
RUN apt-get update && apt-get install -y firefox-esr

# Install Geckodriver
RUN apt-get install -y wget unzip
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
RUN tar -xvzf geckodriver-v0.34.0-linux64.tar.gz
RUN mv geckodriver /usr/local/bin/
RUN chmod +x /usr/local/bin/geckodriver

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python3", "-m", "flask", "--app", "app.routes", "run", "--host=0.0.0.0", "--port=8080"]

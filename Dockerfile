FROM python:3.7

ENV FLASK_APP "/app/server/server.py"

RUN mkdir /app/
WORKDIR /app/
RUN pip install pipenv
COPY Pipfile* /app/
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt
COPY . /app/

EXPOSE 5000
CMD flask run --host=0.0.0.0

# Docker commands to run:
# docker build -f Dockerfile -t smart-stocks:latest .
# docker image ls
# docker run -it --rm --name smart-stocks-container -p 5000:5000 smart-stocks:latest

# Access deployed server at: http://localhost:5000

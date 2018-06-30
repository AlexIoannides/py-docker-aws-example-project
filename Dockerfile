FROM python:3.6.5-slim
WORKDIR /usr/src/app
COPY . .
EXPOSE 5000
RUN pip install pipenv
RUN pipenv install
CMD ["pipenv", "run", "python", "-m", "microservice.api"]

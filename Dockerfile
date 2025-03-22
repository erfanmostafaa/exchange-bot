FROM registry.sedrehgroup.ir/python:3.11.1

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get install -y 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
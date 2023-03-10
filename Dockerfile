FROM python:3.10.4

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 5222/tcp

CMD ["python", "main.py"]
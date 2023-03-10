FROM python:3.10.4

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

#EXPOSE 80/tcp
EXPOSE 443/tcp

CMD ["python", "main.py"]
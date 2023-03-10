FROM python:3.10.4

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8081/tcp

CMD ["python", "main.py"]
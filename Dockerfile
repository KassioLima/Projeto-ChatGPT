FROM python:3.10.4

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 3000

COPY . .

CMD [ "python3", "main.py" ]
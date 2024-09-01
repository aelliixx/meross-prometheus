FROM python:3.12.3

ADD app.py .
ADD requirements.txt .
ADD .env .
RUN pip install -r requirements.txt

CMD ["python", "./app.py"]
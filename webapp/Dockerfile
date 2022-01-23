FROM python:3.9

WORKDIR /webapp

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./src ./src

EXPOSE 5000

CMD ["python", "./src/main.py"]
FROM python:3.13-slim-buster

WORKDIR /code

COPY requirements.txt code/requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
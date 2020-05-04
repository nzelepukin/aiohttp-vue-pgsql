FROM python:3.8.2-buster
WORKDIR /app
COPY ./app/requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python3", "./app.py" ]
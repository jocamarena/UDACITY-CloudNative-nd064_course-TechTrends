FROM python:3.8
LABEL maintainer="Jose Camarena"

COPY ./techtrends /app
WORKDIR /app
RUN pwd
RUN ls -l
RUN python3 --version
RUN pip install -r requirements.txt
RUN python3 init_db.py
EXPOSE 3111


# command to run on container start
CMD [ "python", "app.py" ]
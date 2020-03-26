FROM python:3.8.2-buster

LABEL maintainer="Brenden Hyde"

USER root

RUN apt-get update && apt-get install -y firefox-esr

ENV APP_DIR /app
ENV GECKODRIVER_DIR /app/vendor/geckodriver
ENV PATH $PATH:/app/vendor/geckodriver

RUN mkdir -p $GECKODRIVER_DIR

ADD vendor/geckodriver-v0.26.0-linux64.tar.gz $GECKODRIVER_DIR
RUN chmod +x $GECKODRIVER_DIR/geckodriver

ADD requirements.txt $APP_DIR/
ADD costco-tp.py $APP_DIR/
ADD tp_urls.txt $APP_DIR/

WORKDIR $APP_DIR

RUN pip install -r requirements.txt
CMD ["python", "costco-tp.py"]

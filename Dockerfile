FROM python:3.10

RUN set -xe && \
    apt-get update && \
    apt-get install -y \
        git

# sqlite \
WORKDIR /src
COPY . /src
RUN pip install -r requirements.txt

CMD ["flask", "run"]

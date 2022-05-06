FROM python:3.9.5
WORKDIR /src
RUN apt update
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
COPY requirements.txt /src
RUN pip install -r requirements.txt
COPY . /src
ENV PATH="/mia_venv/bin:${PATH}"
CMD ['python3.9', '-u', 'main_app.py']



FROM python:3.6
WORKDIR /musharing_server

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "start:ser", "-c", "./gunicorn.conf.py"]
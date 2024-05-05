FROM python:3.11

WORKDIR /app

COPY pip.conf /root/.pip/pip.conf

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]

FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /app_dir
WORKDIR /app_dir
COPY requirements.txt /app_dir
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /app_dir
EXPOSE 8091
WORKDIR /app_dir
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8091" ]
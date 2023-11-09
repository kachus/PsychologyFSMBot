FROM python: 3.11
COPY . .
RUN apt-get update -y && apt-get upgrade -y && pip install --upgrade pip  \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt && apt-get install -y ffmpeg \
    && apt-get clean
ENV PYTHONPATH $PYTHONPATH:.
CMD ["python3", "bot.py"]

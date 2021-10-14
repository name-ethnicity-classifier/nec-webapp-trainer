FROM python:3.9
WORKDIR "./app"

COPY . .

RUN apt-get update
RUN apt install libpq-dev

RUN pip install numpy
RUN pip install pandas
RUN pip install matplotlib
RUN pip install uuid
RUN pip install torch==1.9.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install pickle5
RUN pip install tqdm
RUN pip install scikit-learn
RUN pip install psycopg2

CMD ["python", "-u", "./train_jobs.py"]
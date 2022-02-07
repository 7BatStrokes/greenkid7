FROM python:3.8

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN python -m pip install -r requirements.txt
RUN pip install --no-binary=shap 'shap==0.39.0' --force-reinstall
#RUN pip install -U numpy

EXPOSE 8080 2222

CMD python main.py
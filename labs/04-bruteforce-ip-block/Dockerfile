FROM python:3.12-alpine
WORKDIR /app
COPY labs/04-bruteforce-ip-block/app.py /app/app.py
COPY common/templates/ /app/templates/
COPY common/static/ /app/static/
COPY common/wordlists/generator.py /app/generator.py
RUN pip install --no-cache-dir flask==3.0.3
RUN python3 generator.py --lab 4 --out /app/static/wordlists
EXPOSE 80
CMD ["python3", "app.py"]

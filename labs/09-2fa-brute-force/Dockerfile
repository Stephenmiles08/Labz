FROM python:3.12-alpine
WORKDIR /app
COPY labs/09-2fa-brute-force/app.py /app/app.py
COPY common/templates/ /app/templates/
COPY common/static/ /app/static/
COPY common/wordlists/generator.py /app/generator.py
COPY common/wheels/ /app/wheels/
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels flask==3.0.3
RUN python3 generator.py --lab 9 --out /app/static/wordlists
EXPOSE 80
CMD ["python3", "app.py"]

FROM python:3.10

WORKDIR /app

COPY Frontend/requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY Frontend/app.py /app/

COPY Frontend/key.json /app/

# Set the environment variable PORT
ENV PORT 8080

# Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port", "8080"]
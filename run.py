# run.py

## $ docker build -t transmission-mgr:latest .
## $ docker run --network="host" -d -p 9200:9200 transmission-mgr


from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9200)

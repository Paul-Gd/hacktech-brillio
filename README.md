## Running the app
1. Install dependencies into venv. Make sure you have python 3.12 installed:
    ```bash
   python3.12 --version
   python3.12 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```
2. Start FastApi server:
    ```bash
   cd api
   python3 -m uvicorn main:app --reload
   ```
   
## Hosting the app
The app is hosted in Heroku at [https://hacktech-brillio-e28a25e2835a.herokuapp.com](https://hacktech-brillio-e28a25e2835a.herokuapp.com).

### OpenAPI Documentation
The OpenAPI documentation is available at [https://hacktech-brillio-e28a25e2835a.herokuapp.com/docs](https://hacktech-brillio-e28a25e2835a.herokuapp.com/docs).

# Models
## Naive bayes
### Short description
### Accuracy
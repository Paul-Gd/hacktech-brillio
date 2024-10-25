## Running the app
1. Install dependencies into venv:
    ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start FastApi server:
    ```bash
   python3 -m uvicorn api.main:app --reload
   ```
   
## Hosting the app
The app is hosted in Heroku at [https://hacktech-brillio-e28a25e2835a.herokuapp.com](https://hacktech-brillio-e28a25e2835a.herokuapp.com)
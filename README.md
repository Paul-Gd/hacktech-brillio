<p align="center">
  <img src="./images/logo.png" />
<h1 align="center">Trusted reviews</h1>
</p>

Introducing our Amazon Review Checker app, designed to help you quickly identify which reviews are trustworthy and which
might be fake. Reviews are highlighted in **green** for verified, reliable reviews and **red** for flagged, suspicious
ones. Each review comes with an explanation and a confidence score, which you can view by hovering over the "View
details" button. The app also calculates a **trust score** for the product and provides a **summary** of the reviews.
You can easily hide flagged reviews by using the **"Hide fake reviews"** button to focus only on trusted feedback.

# Installing the extension

Because we didn't publish the extension on the Chrome Web Store, you need to load the unpacked extension in developer
mode:

1. Download the zip file from the [releases page](https://github.com/Paul-Gd/hacktech-brillio/releases/) and unzip it.
2. Go to the Extensions page by entering chrome://extensions in a new tab. (By design chrome:// URLs are not linkable.)
    - Alternatively, click the Extensions menu puzzle button and select Manage Extensions at the bottom of the menu.
    - Or, click the Chrome menu, hover over More Tools, then select Extensions.
3. Enable Developer Mode by clicking the toggle switch next to Developer mode.
4. Click the Load unpacked button and select the extension directory unzipped at step 1.

# Developing the app

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

The app is hosted in Heroku
at [https://hacktech-brillio-e28a25e2835a.herokuapp.com](https://hacktech-brillio-e28a25e2835a.herokuapp.com).

### OpenAPI Documentation for the API

You can access the OpenAPI documentation
at [https://hacktech-brillio-e28a25e2835a.herokuapp.com/docs](https://hacktech-brillio-e28a25e2835a.herokuapp.com/docs),
making it easy to integrate this API with other platforms.

# Developing the extension

Please check the source code for the extension in the `extension` folder for more info.
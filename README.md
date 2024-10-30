<p align="center">
  <img src="./images/logo.png" />
<h1 align="center">Trusted reviews</h1>
</p>

Introducing our Amazon Review Checker extension, designed to help you quickly identify which reviews are trustworthy and
which
might be fake. Reviews are highlighted in **green** for verified, reliable reviews and **red** for flagged, suspicious
ones. Each review comes with an explanation and a confidence score, which you can view by hovering over the "View
details". The extension also calculates a **trust score** for the product and provides a **summary** of the reviews.
You can easily hide flagged reviews by using the **"Hide fake reviews"** button to focus only on trusted feedback.

# Example

This product is labeled as Mosquito Repellent, however some reviews show pictures of Snake Repellant. This is a
[bait-and-switch listing](https://arstechnica.com/tech-policy/2020/12/amazon-still-hasnt-fixed-its-problem-with-bait-and-switch-reviews/).

In the video bellow you can see that the extension correctly identified those reviews using `gpt-4o-mini`:

https://github.com/user-attachments/assets/1cfa2788-cfab-42b0-bf9a-348b3a79f588

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

⚠️ This app was developed for the [Hack-Tech 2024](https://hack-tech.ai/) Brillio Challenge on fake review detection,
where it won one of the two grand prizes: _the Best Innovation award for Human-Computer Interaction_. Built in just 2 days
and 6 hours, it may not fully adhere to all best practices and guidelines.

## Figma design

The Figma design can be
found [here](https://www.figma.com/design/lqlL85ZXz1xZSefM9OsuOf/Hackathon---Brillio-challenge?node-id=0-1&node-type=canvas).

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
   OPENAI_API_KEY=<api_key> python3 -m uvicorn main:app --reload
   ```

## Hosting the app

The app was hosted in Heroku
at [https://hacktech-brillio-e28a25e2835a.herokuapp.com](https://hacktech-brillio-e28a25e2835a.herokuapp.com).

### OpenAPI Documentation for the API

You can access the OpenAPI documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), making it easy to
integrate this API with other platforms.

# Developing the extension

Please check the source code for the extension in the `extension` folder for more info.

# Contributors

- [AunerArpad](https://github.com/AunerArpad)
- [davidebara](https://github.com/davidebara)
- [sebastianvlad1](https://github.com/sebastianvlad1)
- [Kopa7](https://github.com/Kopa7)
- [vaarga](https://github.com/vaarga)
- [Paul-Gd](https://github.com/Paul-Gd)

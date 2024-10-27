const closeIcon = document.getElementById("close-icon");
const dropdownToggle = document.getElementById("dropdown-toggle");
const dropdownToggleButton = document.getElementById("dropdown-toggle-text");
const dropdownMenu = document.getElementById("dropdown");
const toggleArrow = document.getElementById("arrow");
const preloaderContainer = document.getElementById('preloader-container');
const scoreAndSummaryContainer = document.getElementById('score-and-summary-container');
const score = document.getElementById("score")
const summary = document.getElementById("summary-point")
const hideFakeReviews = document.getElementById("hideFakeReviews")
const hideModelNameEl = document.getElementById('change-model');
let model = "gpt_4o_mini"
let isFetching = false;

const toggleDropdown = function () {
    dropdownMenu.classList.toggle("show");
    toggleArrow.classList.toggle("arrow");
};

hideFakeReviews.addEventListener('change', async function () {
    chrome.storage.sync.set({hideFakeReviews: this.checked});
    const tab = await getActiveTab();
    await executeScriptAsync(tab.id, (hideReview) => {
        const reviewElements = document.querySelectorAll('.review');
        // for each review element, add a class to it, based on reviews.is_computer_generated
        reviewElements.forEach((reviewElement, index) => {
            if (reviewElement.classList.contains('fakeReviewClass')) {
                if (hideReview) {
                    reviewElement.classList.add('hideFakeReview');
                } else {
                    reviewElement.classList.remove('hideFakeReview');
                }
            }
        });
    }, [this.checked]);
});

async function removeElementsAddedByExtension() {
    const tab = await getActiveTab();
    await executeScriptAsync(tab.id, (styleToInject) => {
        document.querySelectorAll('.validCommentReview').forEach(function (element) {
            element.remove();
        });
        document.querySelectorAll('.cgCommentReview').forEach(function (element) {
            element.remove();
        });
        document.querySelectorAll('.fakeReviewClass').forEach(function (element) {
            element.classList.remove('fakeReviewClass');
        });
        document.querySelectorAll('.validReviewClass').forEach(function (element) {
            element.classList.remove('validReviewClass');
        });
        console.log("removing elements added by extension");
    }, []);
}

document.querySelectorAll('.dropdown-option').forEach(function (item) {
    item.addEventListener('click', async function () {
        const selectedValue = this.getAttribute('data-value');
        console.log(`Selected option value: ${selectedValue}`);
        model = selectedValue;

        await removeElementsAddedByExtension();
        await getDataFromWebsiteAndPopulateIt()
    });
});


// Retrieve the stored value on load
chrome.storage.sync.get('hideModelName', ({hideModelName}) => {
    if (hideModelName || false) {
        hideModelNameEl.classList.add("hidden-item");
    } else {
        hideModelNameEl.classList.remove("hidden-item");
    }
    console.log("hideModelName retrieved:", hideModelName);
});

dropdownToggle.addEventListener("click", function (e) {
    e.stopPropagation();

    if( !isFetching) {
        toggleDropdown();
    }
});

document.documentElement.addEventListener("click", function () {
    if (dropdownMenu.classList.contains("show")) {
        toggleDropdown();
    }
});

dropdownMenu.addEventListener("click", function (e) {
    if (e.target && e.target.tagName === "LI") {
        dropdownToggleButton.textContent = e.target.textContent.trim();
        toggleDropdown();
    }
});

closeIcon.addEventListener("click", function () {
  window.close();
});

// Helper function to get the active tab using async/await
async function getActiveTab() {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve(tabs[0]); // Return the active tab
        });
    });
}

// Helper function to execute a script in the tab using async/await
async function executeScriptAsync(tabId, func) {
    return new Promise((resolve, reject) => {
        chrome.scripting.executeScript({
            target: {tabId: tabId}, func: func
        }, (results) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve(results);
        });
    });
}

// Function to retrieve the title of the current tab
async function getTabTitle() {
    try {
        const tab = await getActiveTab();
        const results = await executeScriptAsync(tab.id, () => document.title);

        // // Update the popup with the title
        // if (results && results[0] && results[0].result) {
        //     document.getElementById('pageTitle').textContent = results[0].result;
        // } else {
        //     document.getElementById('pageTitle').textContent = 'Title not found';
        // }
    } catch (error) {
        // console.error('Error retrieving title:', error);
        // document.getElementById('pageTitle').textContent = 'Error retrieving title';
    }
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getTabTitle);

// Helper function to get the active tab using async/await
async function getActiveTab() {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve(tabs[0]); // Return the active tab
        });
    });
}

// Helper function to execute a script in the tab using async/await
async function executeScriptAsync(tabId, func, args) {
    return new Promise((resolve, reject) => {
        chrome.scripting.executeScript({
            target: {tabId: tabId}, func: func, args: args
        }, (results) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve(results);
        });
    });
}

const addFetchingState = () => {
    isFetching = true;
    dropdownToggle.className = 'disabled-cursor';
    toggleArrow.classList.add('disabled-cursor');
    preloaderContainer.className = '';
    scoreAndSummaryContainer.className = 'hidden-item';
}

const removeFetchingState = () => {
    isFetching = false;
    dropdownToggle.className = '';
    toggleArrow.classList.remove('disabled-cursor');
    preloaderContainer.className = 'hidden-item';
    scoreAndSummaryContainer.className = '';
}

const APP_HOST = 'https://hacktech-brillio-e28a25e2835a.herokuapp.com';

async function makePostRequest(extractedData) {
    const url = APP_HOST + '/review_prediction/';

    const data = {
        description: extractedData.description,
        specs: extractedData.specs,
        user_reviews: extractedData.user_reviews,
        prediction_model: model,
        page_url: "string"
    };
    console.log("data to send", data);

    addFetchingState();

    const response = await fetch(url, {
        method: 'POST', body: JSON.stringify(data), headers: {
            'Accept': 'application/json', 'Content-Type': 'application/json',
        },
    });

    removeFetchingState();

    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
}

const stylesInjected = `
.fakeReviewClass {
    border: 1px solid #E22727;
    border-radius: 4px;
    box-shadow: inset 0px 0px 10px #e227275c;
    padding: 8px;
}

.validReviewClass {
    border: 1px solid #46BD72;
    border-radius: 4px;
    box-shadow: inset 0px 0px 10px #46bd7291;
    padding: 8px;
}

.validCommentReview{
    position: absolute;
    top: 0px;
    right: 0px;
    border-radius: 0px 3px 0px 8px;
    border-bottom: 1px solid #46BD72;
    border-left: 1px solid #46BD72;
    background: #E0FFEC;
    display: flex;
    padding: 10px 12px;
    align-items: center;
    gap: 8px;
}

.cgCommentReview{
    position: absolute;
    top: 0px;
    right: 0px;
    border-radius: 0px 3px 0px 8px;
    border-bottom: 1px solid #E22727;
    border-left: 1px solid #E22727;
    background: #FFE0E0;
    display: flex;
    padding: 10px 12px;
    align-items: center;
    gap: 8px;
}

.validReviewIcon{
    padding: 4px;
    border-radius: 16px;
    background: #AEF0C7;
    width: 28px;
    height: 28px;
}

.cgReviewIcon{
    padding: 4px;
    border-radius: 16px;
    background: #F0AEAE;
    width: 28px;
    height: 28px;
}

.commentReviewText{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    gap: 4px;
}

.validReviewTextFirstPar{
    color: #198842;
    font-family: Inter;
    font-size: 12px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
    font-family: sans-serif;
    margin-bottom: 0px;
}

.cgReviewTextFirstPar{
    color: #881919;
    font-family: Inter;
    font-size: 12px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
    font-family: sans-serif;
    margin-bottom: 0px;
}

.validCommentReviewTextSecondPar{
    color: #198842;
    font-family: Inter;
    font-size: 10px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    font-family: sans-serif;
    margin-bottom: 0px;
}

.cgCommentReviewTextSecondPar{
    color: #881919;
    font-family: Inter;
    font-size: 10px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    font-family: sans-serif;
    margin-bottom: 0px;
}

.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 276px;
  background-color: black;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  text-align: left;
  padding: 12px;

  /* Position the tooltip */
  position: absolute;
  z-index: 3;
  top: 26px;
  left: 50%;
  margin-left: -221px; 
}

.tooltip:hover {
  cursor: pointer;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}

.hideFakeReview{
  display: none;
}
`;

function displayScoreAndSummaryInExtension(predictionResponse) {
    if (!predictionResponse.aggregated_review_data ||
        !predictionResponse.aggregated_review_data.adjusted_review_score ||
        !predictionResponse.aggregated_review_data.feedback_from_model) {
        score.className = "na-score";
        summary.textContent = "This model does not include a general summary.";

        return;
    }
    score.textContent = (predictionResponse.aggregated_review_data.adjusted_review_score * 10).toFixed(1);
    summary.textContent = predictionResponse.aggregated_review_data.feedback_from_model;
    console.log("score", predictionResponse.aggregated_review_data.adjusted_review_score * 10);
    if ((predictionResponse.aggregated_review_data.adjusted_review_score * 10) > 8) {
        score.className = "good-score";
        return;
    }
    if ((predictionResponse.aggregated_review_data.adjusted_review_score * 10) > 4) {
        score.className = "medium-score";
        return;
    }
    score.className = "bad-score";
}

async function getDataFromWebsiteAndPopulateIt() {
    try {
        await removeElementsAddedByExtension();
        const tab = await getActiveTab();
        const results = await executeScriptAsync(tab.id, () => {
            // Function to extract product information from amazon.
            // This should be extracted in another function, however it should also be injected in the page.
            function extractProductSpecs() {
                const productInfo = {};

                // Try to select from prodDetails table (if available)
                const prodDetailsTable = document.querySelectorAll('#prodDetails table tr');
                if (prodDetailsTable.length > 0) {
                    prodDetailsTable.forEach(row => {
                        const key = row.querySelector('th').innerText.trim();
                        const value = row.querySelector('td').innerText.trim();
                        productInfo[key] = value;
                    });
                }

                // Try to select from detail bullets (if available)
                const detailBullets = document.querySelectorAll('#detailBullets_feature_div ul li');
                if (detailBullets.length > 0) {
                    detailBullets.forEach(bullet => {
                        const bulletText = bullet.innerText.split(':');
                        if (bulletText.length === 2) {
                            const key = bulletText[0].trim();
                            const value = bulletText[1].trim();
                            productInfo[key] = value;
                        }
                    });
                }

                return productInfo;
            }

            // Function to extract review information
            function extractReviewInformation() {
                const reviews = [];

                // Get all review elements
                const reviewElements = document.querySelectorAll('.review');

                reviewElements.forEach(reviewElement => {
                    // Extract review text (ignore hidden ones)
                    const reviewTextElement = reviewElement.querySelector('.review-text-content:not(.aok-hidden)');
                    const reviewText = reviewTextElement ? reviewTextElement.innerText.trim() : '';

                    // Extract review value (star rating)
                    const reviewRatingElement = reviewElement.querySelector('.review-rating');
                    const reviewValue = reviewRatingElement ? parseInt(reviewRatingElement.innerText.trim().charAt(0)) : null;

                    // Create review object and push it to the reviews array
                    if (reviewText && reviewValue) {
                        reviews.push({
                            text: reviewText, review_value: reviewValue
                        });
                    }
                });

                return reviews;
            }

            // In some rare cases the '#feature-bullets ul.a-unordered-list' doesn't return the description (it will be
            // undefined)
            const description = document.querySelector('#feature-bullets ul.a-unordered-list') &&
                document.querySelector('#feature-bullets ul.a-unordered-list').innerText;
            const specs = extractProductSpecs();
            const user_reviews = extractReviewInformation();
            console.log("results of extraction", {description, specs, user_reviews});
            return {description, specs, user_reviews};
        });


        // Update the popup with the title
        if (results && results[0] && results[0].result) {
            //TODO populate html from this
            // document.getElementById('pageTitle').textContent = results[0].result.title;
        } else {
            //TODO show error
            // document.getElementById('pageTitle').textContent = 'Failed to load reviews';
        }

        const predictionResponse = await makePostRequest(results[0].result);

        console.log("response from server", predictionResponse);

        // Inject the CSS class into the page
        await executeScriptAsync(tab.id, (styleToInject) => {
            // Inject CSS class into the page
            function injectClassAndStyle(style) {
                const targetElement = document.body; // Modify the selector as needed

                // Add a new class to the element
                targetElement.classList.add('injectedClass');

                // Inject the style for that class
                const styleElement = document.createElement('style');
                styleElement.innerHTML = style;
                document.head.appendChild(styleElement);
            }

            injectClassAndStyle(styleToInject)
        }, [stylesInjected]);
        displayScoreAndSummaryInExtension(predictionResponse);

        // Inject the elements into the page
        await executeScriptAsync(tab.id, (predictionResponse) => {
            const reviews = predictionResponse.reviews
            const reviewElements = document.querySelectorAll('.review');
            // for each review element, add a class to it, based on reviews.is_computer_generated
            reviewElements.forEach((reviewElement, index) => {
                console.log("adding class to reviewElement ", reviewElement, predictionResponse);
                if (!reviews[index].is_computer_generated) {
                    reviewElement.classList.add('validReviewClass');
                    // TODO: don't use innerHTML as it's not safe
                    reviewElement.innerHTML += `
                        <div class="validCommentReview">
                            <svg id="Layer_1" class="validReviewIcon" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                                <defs>
                                <style>
                                  .cls-1 {
                                    fill: none;
                                  }
                                </style>
                              </defs>
                              <polygon points="13 24 4 15 5.414 13.586 13 21.171 26.586 7.586 28 9 13 24"/>
                              <rect id="_Transparent_Rectangle_" data-name="&lt;Transparent Rectangle&gt;" class="cls-1" width="32" height="32"/>
                            </svg>
                            <div class="commentReviewText">
                                <p class="validReviewTextFirstPar">Valid review</p>
                                <div class="tooltip">
                                    <p class="validCommentReviewTextSecondPar">View details</p>
                                    <span class="tooltiptext">
                                        <p>${reviews[index].certainty ? `Certainty ${Math.round(reviews[index].certainty * 100)}%` : "Review details"}</p>
                                        <p>${reviews[index].feedback_from_model ? reviews[index].feedback_from_model : "Missing feedback"}</p>
                                    </span>
                                </div>
                            </div>
                        </div>`;
                } else {
                    reviewElement.classList.add('fakeReviewClass');
                    // reviewElement.classList.add('hideFakeReview');
                    reviewElement.innerHTML += `
                        <div class="cgCommentReview">
                            <svg id="icon" class="cgReviewIcon" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                              <defs>
                                <style>
                                  .cls-1 {
                                    fill: none;
                                  }
                                </style>
                              </defs>
                              <polygon points="17.4141 16 24 9.4141 22.5859 8 16 14.5859 9.4143 8 8 9.4141 14.5859 16 8 22.5859 9.4143 24 16 17.4141 22.5859 24 24 22.5859 17.4141 16"/>
                              <g id="_Transparent_Rectangle_" data-name="&amp;lt;Transparent Rectangle&amp;gt;">
                                <rect class="cls-1" width="32" height="32"/>
                              </g>
                            </svg>
                            <div class="commentReviewText">
                                <p class="cgReviewTextFirstPar">Fake review</p>
                                <div class="tooltip">
                                    <p class="cgCommentReviewTextSecondPar">View details</p>
                                    <span class="tooltiptext">
                                        <p>${reviews[index].certainty ? `Certainty ${Math.round(reviews[index].certainty * 100)}%` : "Review details"}</p>
                                        <p>${reviews[index].feedback_from_model ? reviews[index].feedback_from_model : "Missing feedback"}</p>
                                    </span>
                                </div>
                            </div>
                        </div>`;
                }
            });
        }, [predictionResponse]);

    } catch (error) {
        console.error('Error retrieving title:', error);
        document.getElementById('pageTitle').textContent = 'Error retrieving title';
        throw error;
    }
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getDataFromWebsiteAndPopulateIt);

// // Initialize button with users' preferred color
const changeColor = document.getElementById('changeColor');

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

const APP_HOST = 'https://hacktech-brillio-e28a25e2835a.herokuapp.com';

async function makePostRequest(extractedData) {
    const url = APP_HOST + '/review_prediction/';

    const data = {
        description: extractedData.description,
        specs: extractedData.specs,
        user_reviews: extractedData.user_reviews,
        prediction_model: "random",
        page_url: "string"
    };

    const response = await fetch(url, {
        method: 'POST', body: JSON.stringify(data), headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    });
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

.commentReview{
    position: absolute;
    top: 0px;
    right: 0px;
    border-radius: 0px 0px 0px 8px;
    border: 1px solid #46BD72;
    background: #E0FFEC;
    display: flex;
    padding: 10px 12px;
    align-items: center;
    gap: 8px;
}
.commentValidReviewIcon{
    padding: 4px;
    border-radius: 16px;
    background: #AEF0C7;
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

.commentReviewTextFirstPar{
    color: #198842;
    font-family: Inter;
    font-size: 12px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
    font-family: sans-serif;
    margin-bottom: 0px;
}
.commentReviewTextSecondPar{
    color: #198842;
    font-family: Inter;
    font-size: 10px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    font-family: sans-serif;
    margin-bottom: 0px;
}
`;

async function getDataFromWebsiteAndPopulateIt() {
    try {
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

            const description = document.querySelector('#feature-bullets ul.a-unordered-list').innerText;
            const specs = extractProductSpecs();
            const user_reviews = extractReviewInformation();
            console.log("results of extraction", {description, specs, user_reviews});
            return {description, specs, user_reviews};
        });


        // Update the popup with the title
        if (results && results[0] && results[0].result) {
            document.getElementById('pageTitle').textContent = results[0].result.title;
        } else {
            document.getElementById('pageTitle').textContent = 'Failed to load reviews';
        }

        // const predictionResponse = await makePostRequest(results[0].result);
        const predictionResponse = {
            "reviews": [
                {
                    "is_computer_generated": false,
                    "feedback_from_model": "grape",
                    "certainty": null
                },
                {
                    "is_computer_generated": false,
                    "feedback_from_model": "orange",
                    "certainty": null
                },
                {
                    "is_computer_generated": true,
                    "feedback_from_model": "grape",
                    "certainty": null
                },
                {
                    "is_computer_generated": true,
                    "feedback_from_model": "watermelon",
                    "certainty": null
                },
                {
                    "is_computer_generated": false,
                    "feedback_from_model": "blueberry",
                    "certainty": null
                },
                {
                    "is_computer_generated": true,
                    "feedback_from_model": "orange",
                    "certainty": null
                },
                {
                    "is_computer_generated": true,
                    "feedback_from_model": "grape",
                    "certainty": null
                },
                {
                    "is_computer_generated": false,
                    "feedback_from_model": "grape",
                    "certainty": null
                },
                {
                    "is_computer_generated": true,
                    "feedback_from_model": "mango",
                    "certainty": null
                },
                {
                    "is_computer_generated": false,
                    "feedback_from_model": "mango",
                    "certainty": null
                }
            ],
            "aggregated_review_data": null
        }
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

        // Inject the elements into the page
        await executeScriptAsync(tab.id, (predictionResponse) => {
            const reviews = predictionResponse.reviews
            const reviewElements = document.querySelectorAll('.review');
            // for each review element, add a class to it, based on reviews.is_computer_generated
            reviewElements.forEach((reviewElement, index) => {
                console.log("adding class to reviewElement ", reviewElement, predictionResponse);
                if (reviews[index].is_computer_generated) {
                    reviewElement.classList.add('fakeReviewClass');
                    reviewElement.innerHTML += `<div class="commentReview">
                            <svg id="Layer_1" class="commentValidReviewIcon" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
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
                                <p class="commentReviewTextFirstPar">Valid review</p>
                                <p class="commentReviewTextSecondPar">View details</p>
                            </div>
                        </div>`;
                } else {
                    reviewElement.classList.add('validReviewClass');
                }
            });

            injectClassAndStyle(styleToInject)
        }, [predictionResponse]);

    } catch (error) {
        console.error('Error retrieving title:', error);
        document.getElementById('pageTitle').textContent = 'Error retrieving title';
        throw error;
    }
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getDataFromWebsiteAndPopulateIt);

changeColor.addEventListener('click', getDataFromWebsiteAndPopulateIt);


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
        prediction_model: "naive_bayes",
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
}

.validReviewClass {
    border: 1px solid #46BD72;
    border-radius: 4px;
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

        const response = await makePostRequest(results[0].result);
        console.log("response from server", response);
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
    } catch (error) {
        console.error('Error retrieving title:', error);
        document.getElementById('pageTitle').textContent = 'Error retrieving title';
        throw error;
    }
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getDataFromWebsiteAndPopulateIt);

changeColor.addEventListener('click', getDataFromWebsiteAndPopulateIt);


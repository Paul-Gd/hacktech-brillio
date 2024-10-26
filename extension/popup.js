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
async function executeScriptAsync(tabId, func) {
    return new Promise((resolve, reject) => {
        chrome.scripting.executeScript({
            target: {tabId: tabId},
            func: func
        }, (results) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve(results);
        });
    });
}


// Function to retrieve the title of the current tab
async function getDataFromWebsiteAndPopulateIt() {
    try {
        const tab = await getActiveTab();
        const results = await executeScriptAsync(tab.id, () => {
            // Function to extract product information from amazon.
            // This should be extracted in another function
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
                            review_text: reviewText,
                            review_value: reviewValue
                        });
                    }
                });

                return reviews;
            }

            const description = document.querySelector('#feature-bullets ul.a-unordered-list').innerText;
            const specs = extractProductSpecs();
            const reviews = extractReviewInformation();
            return {description, specs, reviews};
        });
        console.log("results", results[0]);

        // Update the popup with the title
        if (results && results[0] && results[0].result) {
            document.getElementById('pageTitle').textContent = results[0].result.title;
        } else {
            document.getElementById('pageTitle').textContent = 'Failed to retrieve data';
        }
    } catch (error) {
        console.error('Error retrieving title:', error);
        document.getElementById('pageTitle').textContent = 'Error retrieving title';
        throw error;
    }
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getDataFromWebsiteAndPopulateIt);

changeColor.addEventListener('click', getDataFromWebsiteAndPopulateIt);


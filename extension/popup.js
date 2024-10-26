// // Initialize button with users' preferred color
// const changeColor = document.getElementById('changeColor');
// const changeModel = document.getElementById('changeModel');
//
// chrome.storage.sync.get('color', ({color}) => {
//     changeColor.style.backgroundColor = color;
// });
//
// // When the button is clicked, inject setPageBackgroundColor into current page
// changeColor.addEventListener('click', async () => {
//     const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
//
//     chrome.scripting.executeScript({
//         target: {tabId: tab.id},
//         func: setPageBackgroundColor
//     }).then(injectionResults => {
//             console.log(injectionResults)
//         });
//     chrome.scripting.executeScript({
//         target: {tabId: tab.id},
//         func: getTitle,
//     }).then(injectionResults => {
//         // injectionResults is an array, and the return value from getTitle will be inside its first element's result property
//         const title = injectionResults[0].result;
//         console.log("Page title: ", title);
//     });
//
// });
//
// // The body of this function will be executed as a content script inside the
// // current page
// function setPageBackgroundColor() {
//     chrome.storage.sync.get('color', ({color}) => {
//         document.body.style.backgroundColor = color;
//     });
//     console.log("set page background color");
//     console.log("title", document.title)
// }
//
// function getTitle() { return document.title; }
//
// Helper function to get the active tab using async/await
async function getActiveTab() {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
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
            target: { tabId: tabId },
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
async function getTabTitle() {
    try {
        const tab = await getActiveTab();
        const results = await executeScriptAsync(tab.id, () => document.title);

        // Update the popup with the title
        if (results && results[0] && results[0].result) {
            document.getElementById('pageTitle').textContent = results[0].result;
        } else {
            document.getElementById('pageTitle').textContent = 'Title not found';
        }
    } catch (error) {
        console.error('Error retrieving title:', error);
        document.getElementById('pageTitle').textContent = 'Error retrieving title';
    }
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getTabTitle);


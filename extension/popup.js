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

// Function to retrieve the title of the current tab
function getTabTitle() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs[0]; // Get the active tab
        // Use chrome scripting to inject a script that gets the document's title
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                return document.title;
            } // Injects a script to get the document title
        }, (results) => {
            if (results && results[0] && results[0].result) {
                document.getElementById('pageTitle').textContent = results[0].result; // Update the popup with the title
            } else {
                document.getElementById('pageTitle').textContent = 'Title not found';
            }
        });
    });
}

// Call the function when the popup is loaded
document.addEventListener('DOMContentLoaded', getTabTitle);

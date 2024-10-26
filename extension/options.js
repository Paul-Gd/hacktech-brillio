const hideModelNameEl = document.getElementById('hideModelName');

// Add event listener for changes in checkbox
hideModelNameEl.addEventListener('change', async (event) => {
    const hideModelName = event.target.checked;
    console.log(`Option selected: ${hideModelName}`);
    // Store the checkbox state in chrome storage
    chrome.storage.sync.set({ hideModelName });
});

// Retrieve the stored value on load
chrome.storage.sync.get('hideModelName', ({ hideModelName }) => {
    hideModelNameEl.checked = hideModelName || false;  // Set the checkbox based on stored value
    console.log("hideModelName retrieved:", hideModelName);
});


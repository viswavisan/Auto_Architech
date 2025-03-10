document.addEventListener('DOMContentLoaded', function() {
    const messageBox = document.createElement('div');

    // Create the message box
    messageBox.style.display = 'none';
    messageBox.style.position = 'fixed';
    messageBox.style.top = '20px';
    messageBox.style.right = '20px';
    messageBox.style.padding = '10px';
    messageBox.style.color = 'white'; // Text color
    messageBox.style.borderRadius = '5px';
    messageBox.style.zIndex = '1000';
    messageBox.style.display = 'flex'; // Use flexbox
    messageBox.style.alignItems = 'center'; // Center items vertically
    messageBox.style.justifyContent = 'space-between'; // Space between items

    // Create the close button
    const closeButton = document.createElement('button');
    closeButton.className = 'close-btn';
    closeButton.innerHTML = '×';
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.color = 'white';
    closeButton.style.fontSize = '16px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.marginLeft = '10px'; // Add some margin to the left

    closeButton.onclick = closeMessage; // Set the onclick event

    // Create the message text
    const messageText = document.createElement('span'); // Use a span for the message text

    // Create the progress bar
    const progressBar = document.createElement('div');
    progressBar.style.width = '100%';
    progressBar.style.height = '5px';
    progressBar.style.background = 'rgba(255, 255, 255, 0.5)';
    progressBar.style.position = 'relative';
    progressBar.style.overflow = 'hidden';
    progressBar.style.borderRadius = '5px';
    progressBar.style.marginTop = '5px';

    // Create the progress indicator
    const progress = document.createElement('div');
    progress.style.height = '100%';
    progress.style.background = 'white';
    progress.style.width = '0'; // Start at 0%
    progress.style.position = 'absolute';
    progress.style.left = '0';
    progress.style.top = '0';
    progress.style.transition = 'width 3s linear'; // Animate width change

    // Append elements to the message box
    messageBox.appendChild(messageText);
    messageBox.appendChild(closeButton);
    document.body.appendChild(messageBox);
    messageBox.appendChild(progressBar);
    progressBar.appendChild(progress);

    // Define the showMessage function with parameters for text and color
    window.showMessage = function(text = '', color = '#f44336',position='top') {
        messageBox.style.display = 'block';
        messageBox.style.background = color; // Set the background color
        messageText.textContent = text; // Set the message text
        if (position=='top'){
            messageBox.style.top = '20px';
            messageBox.style.right = '20px';
        }
        else if (position=='center'){
            messageBox.style.top = '50%';
            messageBox.style.right = '50%';
            messageBox.style.transform = 'translate(50%, -50%)'; 
        }

        setTimeout(() => {progress.style.width = '100%'; }, 10); 
        const closeTimeout = setTimeout(() => {closeMessage();}, 3000); 
        messageBox.dataset.closeTimeout = closeTimeout;
    };

    // Define the closeMessage function
    function closeMessage() {
        messageBox.style.display = 'none';
        progress.style.width = '0'; 
        clearTimeout(messageBox.dataset.closeTimeout); 
    }
});


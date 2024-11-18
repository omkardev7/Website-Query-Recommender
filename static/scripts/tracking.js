(function () {
    // Generate a unique session ID
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = 'sess-' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('sessionId', sessionId);
    }

    // Time tracking variables
    let startTime = Date.now();
    let totalTimeSpent = 0;

    // Collect metadata about the page
    function collectMetadata() {
        return {
            title: document.title,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            referrer: document.referrer || 'Direct',
            sessionId: sessionId
        };
    }

    // Store data locally in localStorage
    function storeData(key, data) {
        const existingData = JSON.parse(localStorage.getItem(key)) || [];
        existingData.push(data);
        localStorage.setItem(key, JSON.stringify(existingData));
    }

    // Track page visit
    function trackPageVisit() {
        const metadata = collectMetadata();
        metadata.eventType = 'Page Visit';
        metadata.timeSpent = totalTimeSpent; // Save time spent from last page load
        storeData('sessionTrackingData', metadata);
    }

    // Update time spent on page unload
    function updateTimeSpent() {
        totalTimeSpent += Date.now() - startTime;
        sessionStorage.setItem('totalTimeSpent', totalTimeSpent);
    }

    // Track scroll depth
    function trackScrollDepth() {
        const scrollDepth = Math.max(
            window.scrollY + window.innerHeight,
            document.documentElement.scrollHeight
        );
        const scrollPercentage = Math.min(
            100,
            (scrollDepth / document.documentElement.scrollHeight) * 100
        ).toFixed(2);
        const metadata = {
            sessionId: sessionId,
            eventType: 'Scroll Depth',
            scrollPercentage: scrollPercentage + '%',
            timestamp: new Date().toISOString()
        };
        storeData('sessionTrackingData', metadata);
    }

    // Track click events
    function trackClick(event) {
        const metadata = {
            sessionId: sessionId,
            eventType: 'Click',
            elementTag: event.target.tagName,
            elementClasses: event.target.className || 'No classes',
            elementId: event.target.id || 'No ID',
            timestamp: new Date().toISOString()
        };
        storeData('sessionTrackingData', metadata);
    }

    // Event listeners for scroll and click tracking
    window.addEventListener('scroll', trackScrollDepth);
    window.addEventListener('click', trackClick);

    // Track page visit on load
    window.addEventListener('load', trackPageVisit);

    // Update time spent on page unload
    window.addEventListener('beforeunload', updateTimeSpent);

    // Function to download tracking data and metadata as JSON
    function downloadTrackingData() {
        const metadata = collectMetadata(); // Collect only the latest metadata
        
        if (metadata) {
            const blob = new Blob([JSON.stringify(metadata, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
    
            // Create a temporary link element for download
            const a = document.createElement('a');
            a.href = url;
            a.download = 'metadataOnly.json';
            document.body.appendChild(a);
            a.click();
    
            // Clean up
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } else {
            alert('No metadata available to download.');
        }
    }

    // Create a download button (optional, can be added anywhere in your HTML)
    window.addEventListener('load', function () {
        const button = document.createElement('button');
        button.textContent = 'Download Tracking Data';

    // Add a class for styling
    button.classList.add('tracking-button');

    button.onclick = downloadTrackingData;
    document.body.appendChild(button);
    });
})();

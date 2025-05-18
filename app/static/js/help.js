// Help page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Function to update UI based on mood
    function updateUIBasedOnMood(mood) {
        const container = document.querySelector('.container');
        const supportHeader = document.querySelector('h1');
        
        // Remove any existing mood-based classes
        container.classList.remove(
            'border-green-200', 'border-yellow-200', 'border-red-200',
            'dark:border-green-800', 'dark:border-yellow-800', 'dark:border-red-800'
        );
        
        // Add appropriate mood-based styling
        if (mood !== null) {
            if (mood >= 7) {
                container.classList.add('border-green-200', 'dark:border-green-800');
            } else if (mood >= 4) {
                container.classList.add('border-yellow-200', 'dark:border-yellow-800');
            } else {
                container.classList.add('border-red-200', 'dark:border-red-800');
                // Show more prominent emergency contacts for low mood
                document.querySelector('.emergency-contacts').classList.add('scale-105', 'shadow-lg');
            }
        }
    }

    // Function to fetch and update help page statistics
    async function updateHelpStats() {
        try {
            const response = await fetch('/api/help/stats');
            const stats = await response.json();
            
            // Update stats in the UI if elements exist
            const statsContainer = document.querySelector('.help-stats');
            if (statsContainer) {
                statsContainer.innerHTML = `
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                        Total visits: ${stats.total_accesses}
                        <span class="mx-2">•</span>
                        Last 7 days: ${stats.recent_accesses}
                    </p>
                `;
            }
        } catch (error) {
            console.error('Error fetching help stats:', error);
        }
    }

    // Initialize help page
    async function initializePage() {
        // Get recent mood from the data attribute
        const recentMood = document.querySelector('[data-recent-mood]')?.dataset.recentMood;
        if (recentMood) {
            updateUIBasedOnMood(parseFloat(recentMood));
        }
        
        // Update help statistics
        await updateHelpStats();
    }

    // Initialize the page
    initializePage();

    // Add click handlers for contact links
    document.querySelectorAll('a[href^="tel:"]').forEach(link => {
        link.addEventListener('click', function(e) {
            // Track contact interaction
            fetch('/api/help/interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: 'phone',
                    contact: this.href.replace('tel:', '')
                })
            }).catch(console.error);
        });
    });
}); 
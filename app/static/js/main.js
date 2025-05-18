// Handle mood form submission
document.addEventListener('DOMContentLoaded', function() {
    const moodForm = document.getElementById('moodForm');
    const entriesList = document.getElementById('entriesList');
    const todayMood = document.getElementById('todayMood');
    const helpSuggestion = document.getElementById('helpSuggestion');

    // Function to update help suggestion based on mood
    function updateHelpSuggestion(moodScore) {
        if (!helpSuggestion) return;
        
        if (moodScore <= 4) {
            helpSuggestion.classList.remove('hidden');
            helpSuggestion.querySelector('a').classList.add('text-red-600', 'hover:text-red-800');
            helpSuggestion.querySelector('a').classList.remove('text-blue-600', 'hover:text-blue-800');
        } else {
            helpSuggestion.classList.add('hidden');
        }
    }

    // Function to update today's mood display
    async function updateTodayMood() {
        if (!todayMood) return;
        
        try {
            const response = await fetch('/api/moods');
            const entries = await response.json();
            
            if (entries.length > 0) {
                const latestEntry = entries[0];
                const moodScore = latestEntry.mood_score;
                
                // Update mood display
                todayMood.textContent = `${moodScore}/10`;
                
                // Set color based on mood
                if (moodScore <= 3) {
                    todayMood.className = 'text-lg font-semibold text-red-600';
                } else if (moodScore <= 6) {
                    todayMood.className = 'text-lg font-semibold text-yellow-600';
                } else {
                    todayMood.className = 'text-lg font-semibold text-green-600';
                }
                
                // Update help suggestion
                updateHelpSuggestion(moodScore);
            }
        } catch (error) {
            console.error('Error fetching mood:', error);
            todayMood.textContent = '-';
        }
    }

    if (moodForm) {
        moodForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const moodScore = document.getElementById('moodScore').value;
            const note = document.getElementById('note').value;
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            
            try {
                const response = await fetch('/api/mood', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': csrfToken
                    },
                    body: JSON.stringify({
                        mood_score: parseInt(moodScore),
                        note: note
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to save mood entry');
                }
                
                // Clear form
                document.getElementById('note').value = '';
                document.getElementById('moodScore').value = '5';
                document.getElementById('moodScoreValue').textContent = '5';
                
                // Refresh entries list and today's mood
                loadMoodEntries();
                updateTodayMood();
                
                alert('Mood entry saved successfully!');
            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'Failed to save mood entry. Please try again.');
            }
        });
    }

    // Load mood entries if we're on the mood journal page
    if (entriesList) {
        loadMoodEntries();
    }

    // Update today's mood on page load
    updateTodayMood();
});

// Function to load mood entries
async function loadMoodEntries() {
    const entriesList = document.getElementById('entriesList');
    if (!entriesList) return;
    
    try {
        const response = await fetch('/api/moods');
        const entries = await response.json();
        
        if (entries.length === 0) {
            entriesList.innerHTML = '<p class="text-gray-500 text-center py-4">No entries yet. Start tracking your mood!</p>';
            return;
        }
        
        entriesList.innerHTML = entries.map(entry => {
            const moodLevel = entry.mood_score <= 3 ? 'low' : entry.mood_score <= 7 ? 'medium' : 'high';
            const date = new Date(entry.timestamp).toLocaleString();
            
            let moodColor;
            if (entry.mood_score <= 3) {
                moodColor = 'text-red-600';
            } else if (entry.mood_score <= 6) {
                moodColor = 'text-yellow-600';
            } else {
                moodColor = 'text-green-600';
            }
            
            return `
                <div class="mood-entry bg-white p-4 rounded-lg shadow" data-mood="${moodLevel}">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <span class="font-semibold ${moodColor}">Mood Score: ${entry.mood_score}/10</span>
                            <span class="text-gray-500 text-sm ml-4">${date}</span>
                        </div>
                    </div>
                    <p class="text-gray-700">${entry.note || 'No notes provided'}</p>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error:', error);
        entriesList.innerHTML = '<p class="text-red-500 text-center py-4">Failed to load entries. Please try again later.</p>';
    }
} 
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Avatar selection elements
    const prevButton = document.getElementById('prevAvatar');
    const nextButton = document.getElementById('nextAvatar');
    const avatarPreview = document.getElementById('avatarPreview');
    const avatarSelect = document.getElementById('avatarSelect');
    const avatarNumber = document.getElementById('avatarNumber');
    const sidebarAvatar = document.getElementById('sidebarAvatar');

    // Question handling elements
    const questionContainer = document.getElementById('dailyQuestion');
    const questionText = document.getElementById('questionText');
    const responseForm = document.getElementById('responseForm');
    const responseInput = document.getElementById('responseInput');

    // Avatar selection handling
    let currentAvatarId = 1;
    const totalAvatars = 10; // Total number of predefined avatars

    function updateAvatarDisplay() {
        console.log('Updating avatar to:', currentAvatarId); // Debug log
        const avatarPath = `/static/avatars/avatar${currentAvatarId}.png`;
        avatarPreview.src = avatarPath;
        avatarSelect.value = currentAvatarId;
        avatarNumber.textContent = `Avatar ${currentAvatarId}`;

        // Debug: Check if image loads successfully
        avatarPreview.onerror = function() {
            console.error('Failed to load avatar image:', avatarPath);
        };
        avatarPreview.onload = function() {
            console.log('Avatar image loaded successfully:', avatarPath);
        };
    }

    if (prevButton && nextButton) {
        console.log('Setting up avatar navigation buttons'); // Debug log

        prevButton.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent any default button behavior
            console.log('Previous button clicked'); // Debug log
            currentAvatarId = currentAvatarId > 1 ? currentAvatarId - 1 : totalAvatars;
            updateAvatarDisplay();
        });

        nextButton.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent any default button behavior
            console.log('Next button clicked'); // Debug log
            currentAvatarId = currentAvatarId < totalAvatars ? currentAvatarId + 1 : 1;
            updateAvatarDisplay();
        });

        // Initialize first avatar
        updateAvatarDisplay();
    } else {
        console.log('Avatar navigation buttons not found'); // Debug log
    }

    // Initialize sidebar if on main pages
    if (sidebarAvatar) initializeSidebar();

    async function initializeSidebar() {
        try {
            // Load user's avatar
            const avatarResponse = await fetch('/api/user/avatar', {
                headers: { 'X-CSRF-TOKEN': csrfToken }
            });
            if (!avatarResponse.ok) throw new Error('Failed to fetch user avatar');
            
            const avatarData = await avatarResponse.json();
            sidebarAvatar.src = `/static/avatars/${avatarData.filename}`;
            
            // Load daily question
            await loadDailyQuestion();
        } catch (error) {
            console.error('Error initializing sidebar:', error);
        }
    }

    async function loadDailyQuestion() {
        try {
            const response = await fetch('/api/random_question', {
                headers: { 'X-CSRF-TOKEN': csrfToken }
            });
            if (!response.ok) throw new Error('Failed to fetch daily question');
            
            const question = await response.json();
            if (question && questionText) {
                questionText.textContent = question.text;
                questionContainer.dataset.questionId = question.id;
                questionContainer.style.display = 'block';
            } else if (questionContainer) {
                questionContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading daily question:', error);
            if (questionContainer) questionContainer.style.display = 'none';
        }
    }

    // Handle question response submission
    if (responseForm) {
        responseForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const questionId = questionContainer.dataset.questionId;
            const response = responseInput.value.trim();
            
            if (!response) return;

            try {
                const result = await fetch('/api/answer_question', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': csrfToken
                    },
                    body: JSON.stringify({
                        question_id: questionId,
                        response: response
                    })
                });

                if (!result.ok) throw new Error('Failed to submit response');

                // Clear input and load new question
                responseInput.value = '';
                await loadDailyQuestion();

            } catch (error) {
                console.error('Error submitting response:', error);
                alert('Failed to submit response. Please try again.');
            }
        });
    }
}); 
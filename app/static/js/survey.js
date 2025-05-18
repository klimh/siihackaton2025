// Survey form functionality
document.addEventListener('DOMContentLoaded', function() {
    const surveyForm = document.getElementById('surveyForm');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');

    // Function to show a message element
    function showMessage(element, duration = 3000) {
        element.classList.remove('hidden');
        setTimeout(() => {
            element.classList.add('hidden');
        }, duration);
    }

    // Function to get today's date in YYYY-MM-DD format
    function getTodayDate() {
        const today = new Date();
        return today.toISOString().split('T')[0];
    }

    // Function to get selected activities
    function getSelectedActivities() {
        const checkboxes = document.querySelectorAll('input[name="activities"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Function to get custom activities
    function getCustomActivities() {
        const inputs = document.querySelectorAll('input[name="custom_activities"]');
        return Array.from(inputs)
            .map(input => input.value.trim())
            .filter(value => value.length > 0);
    }

    // Function to get social media time
    function getSocialMediaTime() {
        const radio = document.querySelector('input[name="social_media_time"]:checked');
        return radio ? radio.value : null;
    }

    // Function to validate form
    function validateForm() {
        const activities = getSelectedActivities();
        const socialMediaTime = getSocialMediaTime();

        if (activities.length === 0) {
            throw new Error('Please select at least one activity');
        }

        if (!socialMediaTime) {
            throw new Error('Please select your social media usage time');
        }

        return true;
    }

    // Function to load existing survey data
    async function loadTodaySurvey() {
        try {
            const response = await fetch(`/api/survey/${getTodayDate()}`);
            if (!response.ok) {
                if (response.status !== 404) {
                    console.error('Error fetching survey:', response.statusText);
                }
                return;
            }

            const data = await response.json();
            
            // Set activities
            data.activities.forEach(activityId => {
                const checkbox = document.getElementById(`activity_${activityId}`);
                if (checkbox) checkbox.checked = true;
            });

            // Set custom activities
            if (data.custom_activities) {
                const inputs = document.querySelectorAll('input[name="custom_activities"]');
                data.custom_activities.forEach((activity, index) => {
                    if (inputs[index]) inputs[index].value = activity;
                });
            }

            // Set social media time
            const radio = document.querySelector(`input[value="${data.social_media_time}"]`);
            if (radio) radio.checked = true;

            // Disable form if not allowed to edit
            if (!data.can_edit) {
                const inputs = surveyForm.querySelectorAll('input, button');
                inputs.forEach(input => input.disabled = true);
                surveyForm.querySelector('button[type="submit"]').textContent = 'Survey Already Submitted';
            }

        } catch (error) {
            console.error('Error loading survey:', error);
        }
    }

    // Handle form submission
    if (surveyForm) {
        surveyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                validateForm();

                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                const response = await fetch('/api/survey', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': csrfToken
                    },
                    body: JSON.stringify({
                        date: getTodayDate(),
                        activities: getSelectedActivities(),
                        custom_activities: getCustomActivities(),
                        social_media_time: getSocialMediaTime()
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to save survey');
                }

                showMessage(successMessage);
                
                // Disable form after successful submission
                const inputs = surveyForm.querySelectorAll('input, button');
                inputs.forEach(input => input.disabled = true);
                surveyForm.querySelector('button[type="submit"]').textContent = 'Survey Submitted';

            } catch (error) {
                console.error('Error:', error);
                errorMessage.querySelector('span').textContent = error.message || 'Failed to save survey. Please try again.';
                showMessage(errorMessage, 5000);
            }
        });

        // Load existing survey data on page load
        loadTodaySurvey();
    }

    // Add validation feedback for activities
    document.querySelectorAll('input[name="activities"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const activities = getSelectedActivities();
            const submitButton = surveyForm.querySelector('button[type="submit"]');
            submitButton.disabled = activities.length === 0;
        });
    });
}); 
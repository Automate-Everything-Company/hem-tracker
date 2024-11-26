document.addEventListener('DOMContentLoaded', function () {
    const username = document.getElementById('username').value;
    fetchUserDataForPlot(username);
});

function fetchUserDataForPlot(username) {
    fetch(`/api/users/user-data/${username}`)
       .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateFactorLevels(data);
        })
        .catch(error => {
            if (error.message === 'Network response was not ok') {
                    alert('No measurements found for this user. Please add a measurement to proceed.');
                }
            else {
                alert('An unexpected error occurred. Please try again later.');
            }
            console.error('Error fetching user data:', error);
        });
}

function updateFactorLevels(data) {
    const localTime = new Date();
    const currentTime = localTime.toLocaleString('en-US', {
        weekday: 'long', hour: '2-digit', minute: '2-digit', hour12: true
    });

    const decayConstant = data.decayConstant;
    const peakLevel = data.peakLevel;
    const weeklyInfusions = data.weeklyInfusions;

    fetch('api/levels/update-levels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decayConstant, peakLevel, weeklyInfusions, currentTime })
    })
    .then(response => response.json())
    .then(data => {
        createOrUpdateDoughnutChart(data);
        plotNewFactorLevelChart(data);
        addHalvingTime(data);
    })
    .catch(error => console.error('Error updating data:', error));
}
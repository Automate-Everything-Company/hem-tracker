document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('signUp').addEventListener('click', function() {
        window.location.href = '/signup';
    });
    fetchDefaultValues();

    document.getElementById('updateButton').addEventListener('click', updateFactorLevels);

    const datetimePickerBtn = document.getElementById('datetimePicker');
    const addDateTimeBtn = document.getElementById('addDateTime');

    if (datetimePickerBtn && addDateTimeBtn) {
        datetimePickerBtn.addEventListener('change', function() {
            if (datetimePickerBtn.value) {
                const dateStr = dateSelection.formatDateTime(datetimePickerBtn.value);
                datetimePickerBtn.dataset.dateStr = dateStr;
                addDateTimeBtn.classList.remove('hidden');
            }
        });
    } else {
        console.error('Buttons not found'); // Debugging
    }
});

async function fetchDefaultValues() {
    try {
        const response = await fetch('data/default-values');
        const data = await response.json();
        document.getElementById('peak_level').value = data.peak_level;
        document.getElementById('time_elapsed').value = data.time_elapsed;
        document.getElementById('second_level_measurement').value = data.second_level_measurement;
        decayConstant = data.decay_constant;
        peakLevel = data.peak_level;
        dateSelection.setInitialDates(data.refill_times);
        updateFactorLevels();
    } catch (error) {
        console.error('Error fetching default data:', error);
    }
}

async function updateFactorLevels() {
    const refillTimes = dateSelection.getRefillTimes();

    const localTime = new Date();
    const currentTime = localTime.toLocaleString('en-US', {
        weekday: 'long', hour: '2-digit', minute: '2-digit', hour12: true
    });

    peakLevel = parseFloat(document.getElementById('peak_level').value);
    timeElapsed = parseFloat(document.getElementById('time_elapsed').value);
    secondLevelMeasurement = parseFloat(document.getElementById('second_level_measurement').value);

    try {
        const decayResponse = await fetch('data/calculate-decay-constant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ peakLevel, timeElapsed, secondLevelMeasurement })
        });

        const decayData = await decayResponse.json();
        const decayConstant = decayData.decay_constant;

        const updateResponse = await fetch('data/update-factor-levels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decayConstant, peakLevel, refillTimes, currentTime })
        });

        const updateData = await updateResponse.json();
        plotNewFactorLevelChart(updateData);
        createOrUpdateDoughnutChart(updateData);

        addHalvingTime(updateData);

    } catch (error) {
        console.error('Error updating data:', error);
    }
}
document.addEventListener('DOMContentLoaded', function () {
    flatpickr("#datetimePickerSignup", {
        enableTime: true,
        dateFormat: "l h:i K", // Monday 03:30 PM
        weekNumbers: true,
        time_24hr: false,
        position: "above",
        onChange: function(selectedDates, dateStr, instance) {
            const datetimePickerBtn = document.getElementById('datetimePickerSignup');
            datetimePickerBtn.innerText = dateStr;

            const addDateTimeBtn = document.getElementById('addDateTimeSignup');
            addDateTimeBtn.classList.remove('hidden');
        }
    });

    const addDateTimeBtn = document.getElementById('addDateTimeSignup');
    const datetimePickerBtn = document.getElementById('datetimePickerSignup');

    if (datetimePickerBtn && addDateTimeBtn) {
        datetimePickerBtn.addEventListener('click', function () {
            addDateTimeBtn.classList.remove('hidden');
        });
        addDateTimeBtn.addEventListener('click', function () {
            addDateTimeSignup();
        });
    } else {
        console.error('Buttons not found'); // Debugging
    }
});

let dates = [];

function addDateTimeSignup() {
    const datetimePicker = document.getElementById('datetimePickerSignup');
    if (datetimePicker.value) {
        dates.push(datetimePicker.value);
        sortDates();
        updateSignupDateList();
        datetimePicker._flatpickr.clear();
        datetimePicker.innerText = `New event`;
    }

    const addDateTimeBtn = document.getElementById('addDateTimeSignup');
    if (addDateTimeBtn) {
        addDateTimeBtn.classList.add('hidden');
    }
}

window.addDateTimeSignup = addDateTimeSignup;

function updateSignupDateList() {
    const selectedDatesDiv = document.getElementById('selectedDatesSignup');
    selectedDatesDiv.innerHTML = '';

    dates.forEach((date, index) => {
        const dateTag = document.createElement('div');
        dateTag.className = 'bg-blue-100 text-blue-800 text-sm font-semibold mr-2 px-2.5 py-0.5 rounded inline-flex items-center';
        dateTag.innerHTML = `
            ${date}
            <button type="button" onclick="removeSignupDate(${index})" class="ml-2 bg-transparent hover:text-red-500 text-red-400">✖</button>
        `;
        selectedDatesDiv.appendChild(dateTag);
    });
}

function removeSignupDate(index) {
    dates.splice(index, 1);
    sortDates();
    updateSignupDateList();
}

function getSignupRefillTimes() {
    return dates;
}
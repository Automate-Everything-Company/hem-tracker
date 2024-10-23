(function() {
    document.addEventListener('DOMContentLoaded', function () {
        const datetimePicker = document.getElementById('datetimePicker');
        const addDateTimeBtn = document.getElementById('addDateTime');

        if (datetimePicker && addDateTimeBtn) {
            datetimePicker.addEventListener('change', function() {
                if (datetimePicker.value) {
                    const dateStr = formatDateTime(datetimePicker.value);
                    datetimePicker.dataset.dateStr = dateStr;
                    addDateTimeBtn.classList.remove('hidden');
                }
            });
        } else {
            console.error('Add DateTime Button not found'); // Debugging
        }
    });

    let dateSelectionDates = [];

    function formatDateTime(value) {
        const date = new Date(value);
        const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        const day = daysOfWeek[date.getDay()];

        let hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'

        return `${day} ${hours}:${minutes} ${ampm}`;
    }

    function addDateTime() {
        const datetimePicker = document.getElementById('datetimePicker');
        if (datetimePicker.dataset.dateStr) {
            dateSelectionDates.push(datetimePicker.dataset.dateStr);
            sortDates(dateSelectionDates);
            updateDateList();
            datetimePicker.value = '';
            datetimePicker.dataset.dateStr = '';
        }

        const addDateTimeBtn = document.getElementById('addDateTime');
        if (addDateTimeBtn) {
            addDateTimeBtn.classList.add('hidden');
        }
    }

    function updateDateList() {
        const selectedDatesDiv = document.getElementById('selectedDates');
        if (!selectedDatesDiv) {
            console.error('Element with id "selectedDates" not found.');
            return;
        }
        selectedDatesDiv.innerHTML = '';

        dateSelectionDates.forEach((date, index) => {
            const dateTag = document.createElement('div');
            dateTag.className = 'bg-blue-100 text-blue-800 text-sm font-semibold mr-2 px-2.5 py-0.5 rounded inline-flex items-center';
            dateTag.innerHTML = `
                ${date}
                <button onclick="dateSelection.removeDate(${index})" class="ml-2 bg-transparent hover:text-red-500 text-red-400">✖</button>
            `;
            selectedDatesDiv.appendChild(dateTag);
        });
    }

    function removeDate(index) {
        dateSelectionDates.splice(index, 1);
        sortDates(dateSelectionDates);
        updateDateList();
    }

    function setInitialDates(initialDates) {
        dateSelectionDates = initialDates;
        sortDates(dateSelectionDates);
        updateDateList();
    }

    function getWeeklyInfusions() {
        return dateSelectionDates;
    }

    window.dateSelection = {
        addDateTime,
        setInitialDates,
        getWeeklyInfusions,
        removeDate,
        formatDateTime,
        getDates: function() { return dateSelectionDates; },
        setDates: function(dates) { dateSelectionDates = dates; }
    };
})();

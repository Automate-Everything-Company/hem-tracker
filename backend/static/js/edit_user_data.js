(function() {
    let isEditMode = false;

    document.addEventListener('DOMContentLoaded', function () {
        const username = document.getElementById('username').value;
        fetchUserData(username);
        setEditButtonHandler();
        setSaveButtonHandler();
        setCancelButtonHandler();
        setupAddDateTimeButton();
    });

    function fetchUserData(username) {
        fetchWithToken(`/api/users/${username}/data`)
            .then(checkResponseStatus)
            .then(response => response.json())
            .then(setUserData)
            .catch(handleError);
    }

    function checkResponseStatus(response) {
        if (!response.ok) {
            if (response.status === 401) {
                logout();
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response;
    }

    function setUserData(data) {
        document.getElementById('email').value = data.email;
        document.getElementById('first_name').value = data.first_name;
        document.getElementById('last_name').value = data.last_name;
        document.getElementById('peak_level').value = data.peak_level;
//        dateSelection.setInitialDates(data.weekly_infusions.split(', '));  // todo: replace with list
        dateSelection.setInitialDates(data.weekly_infusions);
        toggleRemoveButtons();
        hideInputElements();
    }

    function saveUserData() {
        const userData = {
            username:  document.getElementById('username').value,
            email: document.getElementById('email').value,
            first_name: document.getElementById('first_name').value,
            last_name: document.getElementById('last_name').value,
            peak_level: parseFloat(document.getElementById('peak_level').value),
            weekly_infusions: dateSelection.getRefillTimes()
        };

        fetchWithToken(`/api/users/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })
            .then(response => response.json())
            .then(() => {
                hideInputElements();
                window.location.reload();
            })
            .catch(handleError);
    }

    function cancelChanges() {
        const username = document.getElementById('username').value;
        fetchUserData(username);
        hideInputElements();
        toggleRemoveButtons();
    }

    function hideInputElements() {
        setInputReadonly(document.getElementById('email'));
        setInputReadonly(document.getElementById('first_name'));
        setInputReadonly(document.getElementById('last_name'));
        setInputReadonly(document.getElementById('peak_level'));

        document.querySelectorAll('.remove-date-button').forEach(hideElement);

        hideElement(document.getElementById('saveButton'));
        hideElement(document.getElementById('add_event'));
        hideElement(document.getElementById('cancelButton'));
        hideElement(document.getElementById('deleteButton'));
        showElement(document.getElementById('editButton'));
    }

    function setInputReadonly(input) {
        input.setAttribute('readonly', 'true');
        input.classList.replace('text-blue-800', 'text-gray-500');
    }

    function setInputEditable(input) {
        input.removeAttribute('readonly');
        input.classList.replace('text-gray-500', 'text-blue-800');
    }

    function hideElement(element) {
        element.classList.add('hidden');
    }

    function showElement(element) {
        element.classList.remove('hidden');
    }

    function setupAddDateTimeButton() {
        document.getElementById('addDateTime').addEventListener('click', dateSelection.addDateTime);
    }

    function setEditButtonHandler() {
        document.getElementById('editButton').addEventListener('click', function () {
            setInputEditable(document.getElementById('email'));
            setInputEditable(document.getElementById('first_name'));
            setInputEditable(document.getElementById('last_name'));
            setInputEditable(document.getElementById('peak_level'));

            document.querySelectorAll('.remove-date-button').forEach(showElement);

            showElement(document.getElementById('saveButton'));
            showElement(document.getElementById('cancelButton'));
            showElement(document.getElementById('deleteButton'));
            showElement(document.getElementById('add_event'));
            hideElement(document.getElementById('editButton'));

            isEditMode = true;
        });
    }

    function setSaveButtonHandler() {
        document.getElementById('saveButton').addEventListener('click', function() {
            saveUserData();
            isEditMode = false;
            toggleRemoveButtons();
        });
    }

    function setCancelButtonHandler() {
        document.getElementById('cancelButton').addEventListener('click', function() {
            cancelChanges();
            isEditMode = false;
            toggleRemoveButtons();
        });
    }

    function handleError(error) {
        console.error('Error:', error);
    }

    function toggleRemoveButtons() {
        const removeButtons = document.querySelectorAll('.remove-date-button');
        removeButtons.forEach(button => {
            if (isEditMode) {
                button.classList.remove('hidden');
            } else {
                button.classList.add('hidden');
            }
        });
    }

    window.removeSignupDate = function(index) {
        dateSelection.removeDate(index);
        toggleRemoveButtons();
    };

    window.getSignupRefillTimes = function() {
        return dateSelection.getWeeklyInfusions();
    };
})();

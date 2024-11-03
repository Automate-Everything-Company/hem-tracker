
function submitSignupForm(event) {
    event.preventDefault();

    const form = document.getElementById('signupForm');
    const formData = new FormData(form);

    const signupData = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        username: formData.get('username'),
        password: formData.get('password'),
        email: formData.get('email'),
        peak_level: formData.get('peak_level'),
        weekly_infusions: getSignupRefillTimes()
    };

    fetch('/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(signupData)
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(error => {
            alert(`Signup failed: ${error.detail}`);
            throw new Error(`Signup failed: ${error.detail}`);
          });
        }
        return response.json();
      })
      .then(data => {
        alert('Account created');
        console.log('Signup successful:', data);
        window.location.href = '/login';
      })
      .catch(error => {
        console.error('Error during signup:', error);
      });
      }


function getSignupRefillTimes() {
    let dateSelectionDates = window.dateSelection.getDates();
    return dateSelectionDates;
}

window.submitSignupForm = submitSignupForm;

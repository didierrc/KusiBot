function setEyeToggleFunctionality() {

    // Select all the passwords eye icons
    const togglePasswordIcons = document.querySelectorAll('span[data-eye]')

    // Add click event to each icon
    togglePasswordIcons.forEach(iconSpan => {

        iconSpan.addEventListener('click', function () {

            // Get the associated input field
            let targetInput = this.parentElement.querySelector('input')
            let icon = this.querySelector('i')
            if (!targetInput) {
                console.error(`Target input element not found.`)
                return
            }

            // If input field is password, change it to text and its icon.
            if (targetInput.type === 'password') {
                targetInput.type = 'text'
                icon.classList.remove('fa-eye')
                icon.classList.add('fa-eye-slash')
                this.setAttribute('title', 'Hide password')
                this.setAttribute('data-eye', 'Enabled')
            } else { // Same as before but viceversa.
                targetInput.type = 'password';
                icon.classList.remove('fa-eye-slash')
                icon.classList.add('fa-eye')
                this.setAttribute('title', 'Show password')
                this.setAttribute('data-eye', 'Disabled')
            }
        })
    })
}

function setPasswordStrengthValidationFunctionality() {

    // Select password input and indicator div
    const passwordInput = document.getElementById('password_register');
    const strengthIndicator = document.getElementById('password-strength-indicator');

    if (passwordInput && strengthIndicator) {

        // Select checks elements
        const checks = {
            length: document.getElementById('length-check'),
            uppercase: document.getElementById('uppercase-check'),
            lowercase: document.getElementById('lowercase-check'),
            number: document.getElementById('number-check'),
            special: document.getElementById('special-check')
        }

        // Whenever the user types a character, change icons from checks
        passwordInput.addEventListener('input', function () {

            const password = this.value

            // Define strength validation criteria
            const validations = {
                length: password.length >= 8,
                uppercase: /[A-Z]/.test(password),
                lowercase: /[a-z]/.test(password),
                number: /[0-9]/.test(password),
                special: /[#?!@$%^&*-]/.test(password)
            };

            // Function to update the UI for a specific check (X or check icon)
            function updateCheck(checkElement, isValid) {
                const icon = checkElement.querySelector('i')
                if (isValid) {
                    checkElement.classList.add('valid')
                    checkElement.classList.remove('invalid')
                    icon.classList.remove('fa-times-circle')
                    icon.classList.add('fa-check-circle')
                } else {
                    checkElement.classList.add('invalid')
                    checkElement.classList.remove('valid')
                    icon.classList.remove('fa-check-circle')
                    icon.classList.add('fa-times-circle')
                }
            }

            // Update UI for each check
            updateCheck(checks.length, validations.length);
            updateCheck(checks.uppercase, validations.uppercase);
            updateCheck(checks.lowercase, validations.lowercase);
            updateCheck(checks.number, validations.number);
            updateCheck(checks.special, validations.special);
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {

    // Password's eye toggle functionality
    setEyeToggleFunctionality()

    // Password's strength validation functionality
    setPasswordStrengthValidationFunctionality()
})
document.addEventListener('DOMContentLoaded', function () {

    // Select all the passwords eye icons
    const togglePasswordIcons = document.querySelectorAll('span[data-eye]')

    // Add click event to each icon
    togglePasswordIcons.forEach(iconSpan => {

        iconSpan.addEventListener('click', function () {

            // Get the associated input field
            let targetInput = this.parentElement.querySelector('input')
            let icon = this.querySelector('i')
            if (!targetInput) {
                console.error(`Target input element not found.`);
                return;
            }

            // If input field is password, change it to text and its icon.
            if (targetInput.type === 'password') {
                targetInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.setAttribute('title', 'Hide password');
                this.setAttribute('data-eye', 'Enabled');
            } else { // Same as before but viceversa.
                targetInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.setAttribute('title', 'Show password');
                this.setAttribute('data-eye', 'Disabled');
            }

            console.log(this)
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    var wrapper = document.getElementById('authWrapper');
    var btnShowSignup = document.getElementById('btnShowSignup');
    var btnShowSignin = document.getElementById('btnShowSignin');

    if (!wrapper || !btnShowSignup || !btnShowSignin) {
        return;
    }

    var animationDelay = 600;
    var isAnimating = false;
    var toggleButtons = [btnShowSignup, btnShowSignin];
    var forms = Array.prototype.slice.call(document.querySelectorAll('.auth-form'));

    function setToggleState(disabled) {
        toggleButtons.forEach(function (button) {
            button.disabled = disabled;
            button.style.opacity = disabled ? '0.7' : '1';
        });
    }

    function focusActiveForm() {
        var activeFormId = wrapper.classList.contains('signup-active') ? 'signupForm' : 'loginForm';
        var activeForm = document.getElementById(activeFormId);
        var firstField = activeForm ? activeForm.querySelector('input, select, textarea') : null;

        if (firstField) {
            firstField.focus();
        }
    }

    function switchPanel(showSignup) {
        var isSignupActive = wrapper.classList.contains('signup-active');

        if (isAnimating || isSignupActive === showSignup) {
            return;
        }

        isAnimating = true;
        setToggleState(true);

        if (showSignup) {
            wrapper.classList.add('signup-active');
        } else {
            wrapper.classList.remove('signup-active');
        }

        window.setTimeout(function () {
            isAnimating = false;
            setToggleState(false);
            focusActiveForm();
        }, animationDelay);
    }

    btnShowSignup.addEventListener('click', function (event) {
        event.preventDefault();
        switchPanel(true);
    });

    btnShowSignin.addEventListener('click', function (event) {
        event.preventDefault();
        switchPanel(false);
    });

    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var submitButton = form.querySelector('button[type="submit"]');

            if (isAnimating) {
                event.preventDefault();
                return;
            }

            if (!submitButton || submitButton.disabled) {
                if (submitButton) {
                    event.preventDefault();
                }
                return;
            }

            submitButton.disabled = true;
            submitButton.classList.add('is-loading');
            submitButton.style.opacity = '0.65';
            submitButton.setAttribute('aria-busy', 'true');
        });
    });
});

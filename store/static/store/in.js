document.addEventListener('DOMContentLoaded', function () {
    var wrapper = document.getElementById('authWrapper');
    var btnShowSignup = document.getElementById('btnShowSignup');
    var btnShowSignin = document.getElementById('btnShowSignin');

    if (!wrapper || !btnShowSignup || !btnShowSignin) {
        console.error('Auth elements not found:', {
            wrapper: !!wrapper,
            btnShowSignup: !!btnShowSignup,
            btnShowSignin: !!btnShowSignin
        });
        return;
    }

    btnShowSignup.addEventListener('click', function () {
        wrapper.classList.add('signup-active');
    });

    btnShowSignin.addEventListener('click', function () {
        wrapper.classList.remove('signup-active');
    });
});

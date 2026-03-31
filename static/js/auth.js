document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('id_password');
    const confirmInput = document.getElementById('id_confirm_password');
    const eyeToggle = document.querySelector('.eye-toggle');
    const strengthBox = document.getElementById('password-strength');
    const matchBox = document.getElementById('password-match');
    const helpBox = document.querySelector('.password-help-box');
    const requirements = Array.from(document.querySelectorAll('.password-requirements li'));

    if (eyeToggle && passwordInput) {
        eyeToggle.addEventListener('click', function () {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            this.textContent = type === 'password' ? '👁' : '🙈';
        });
    }

    function updateStrength() {
        if (!passwordInput) return;
        const value = passwordInput.value;
        const hasLower = /[a-z]/.test(value);
        const hasUpper = /[A-Z]/.test(value);
        const hasNumber = /[0-9]/.test(value);
        const hasSpecial = /[^A-Za-z0-9]/.test(value);
        const hasLength = value.length >= 8;
        const passedAll = hasLower && hasUpper && hasNumber && hasSpecial && hasLength;

        if (strengthBox) {
            if (value.length === 0) {
                strengthBox.className = 'validation-message';
                strengthBox.textContent = '';
            } else if (hasLength) {
                strengthBox.className = 'validation-message success visible';
                strengthBox.textContent = 'Strong password ✔';
            } else {
                strengthBox.className = 'validation-message error visible';
                strengthBox.textContent = 'Password too short ❌';
            }
        }

        requirements.forEach((item) => {
            const text = item.dataset.rule;
            let valid = false;
            if (text === 'lowercase') valid = hasLower;
            if (text === 'uppercase') valid = hasUpper;
            if (text === 'number') valid = hasNumber;
            if (text === 'special') valid = hasSpecial;
            if (text === 'length') valid = hasLength;
            item.classList.toggle('valid', valid);
        });

        if (helpBox) {
            if (passedAll) {
                helpBox.classList.remove('visible');
            } else {
                helpBox.classList.add('visible');
            }
        }

        updateMatch();
    }

    function updateMatch() {
        if (!confirmInput || !matchBox) return;
        const password = passwordInput ? passwordInput.value : '';
        const confirm = confirmInput.value;
        if (confirm.length === 0) {
            matchBox.className = 'validation-message';
            matchBox.textContent = '';
            return;
        }
        if (password === confirm) {
            matchBox.className = 'validation-message success visible';
            matchBox.textContent = 'Passwords matched ✔';
        } else {
            matchBox.className = 'validation-message error visible';
            matchBox.textContent = 'Passwords do not match ❌';
        }
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', updateStrength);
    }
    if (confirmInput) {
        confirmInput.addEventListener('input', updateMatch);
    }

    setTimeout(() => {
        const toasts = document.querySelectorAll('.toast');
        toasts.forEach(toast => {
            toast.style.transition = 'opacity 0.5s ease';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        });
    }, 2000);
});

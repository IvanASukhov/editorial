// forms.js — JS для управления поведением форм

// Предотвращение двойной отправки формы
document.addEventListener('DOMContentLoaded', function () {
    let forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let btn = form.querySelector('[type="submit"], .btn');
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Отправка...';
            }
        });
    });

    // Подсветка обязательных незаполненных полей при отправке
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let ok = true;
            form.querySelectorAll('[required]').forEach(function(input) {
                input.classList.remove('form-error');
                if (!input.value.trim()) {
                    input.classList.add('form-error');
                    ok = false;
                }
            });
            if (!ok) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля!');
                let firstError = form.querySelector('.form-error');
                if (firstError) firstError.focus();
                let btn = form.querySelector('[type="submit"], .btn');
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Отправить';
                }
            }
        });
    });

    // Для всех input с типом file — показывать имя файла рядом с полем
    let fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            let label = input.closest('label') || input.parentNode;
            let filename = input.files.length > 0 ? input.files[0].name : '';
            let span = label.querySelector('.file-name');
            if (!span) {
                span = document.createElement('span');
                span.className = 'file-name';
                label.appendChild(span);
            }
            span.textContent = filename;
        });
    });
});

// Простейший стиль ошибки для обязательных полей (добавить в custom.css или main.css)
/*
.form-error {
    border: 1.5px solid #e14c4c !important;
    background: #fae7e7 !important;
}
*/

// main.js — базовый JS для редакционно-издательского сайта

// Автоматическое скрытие alert-уведомлений через 4 секунды
document.addEventListener('DOMContentLoaded', function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.7s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 700);
        }, 4000);
    });
});

// Подтверждение удаления (например, рукописи, пользователя, новости)
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить этот элемент?');
}

// Переключение вкладок (например, в профиле или админке)
function switchTab(tabId) {
    let tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    let contents = document.querySelectorAll('.tab-content');
    contents.forEach(cont => cont.classList.add('hide'));

    let targetTab = document.getElementById(tabId + '-tab');
    let targetContent = document.getElementById(tabId + '-content');
    if (targetTab && targetContent) {
        targetTab.classList.add('active');
        targetContent.classList.remove('hide');
    }
}

// Пример быстрой проверки, что все обязательные поля формы заполнены
function validateForm(formId) {
    let form = document.getElementById(formId);
    if (!form) return true;
    let required = form.querySelectorAll('[required]');
    for (let i = 0; i < required.length; i++) {
        if (!required[i].value.trim()) {
            alert('Заполните все обязательные поля!');
            required[i].focus();
            return false;
        }
    }
    return true;
}

// Пример: показать/скрыть пароль
function togglePassword(fieldId) {
    let input = document.getElementById(fieldId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}


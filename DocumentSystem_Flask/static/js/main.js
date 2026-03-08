// Основные функции для веб-приложения

// Подтверждение удаления документа
function confirmDelete(event, docId, docTitle) {
    if (!confirm(`Вы уверены, что хотите удалить документ "${docTitle}"?`)) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Автоматическое скрытие flash сообщений через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    // Flash сообщения
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Подсветка активного пункта меню
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Инициализация подсказок Bootstrap
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        tooltips.forEach(function(tooltip) {
            new bootstrap.Tooltip(tooltip);
        });
    }
});

// Функция для копирования текста в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Скопировано в буфер обмена', 'success');
    }).catch(function(err) {
        showNotification('Ошибка при копировании', 'danger');
    });
}

// Показать уведомление
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(function() {
        const closeButton = alertDiv.querySelector('.btn-close');
        if (closeButton) {
            closeButton.click();
        }
    }, 3000);
}

// Функция для обновления статистики на главной странице
function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            // Обновляем счетчики
            const totalElement = document.querySelector('[data-stat="total"]');
            const protocolsElement = document.querySelector('[data-stat="protocols"]');
            const resolutionsElement = document.querySelector('[data-stat="resolutions"]');

            if (totalElement) totalElement.textContent = data.total;
            if (protocolsElement) protocolsElement.textContent = data.protocols;
            if (resolutionsElement) resolutionsElement.textContent = data.resolutions;
        })
        .catch(error => console.error('Error:', error));
}

// Валидация форм на стороне клиента
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                event.preventDefault();
                showNotification('Заполните все обязательные поля', 'warning');
            }
        });
    });
});

// Предзагрузка данных для формы (если есть параметры в URL)
function prefillFormFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const form = document.querySelector('form');

    if (form) {
        urlParams.forEach(function(value, key) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value;
            }
        });
    }
}

// Вызов функции предзагрузки при загрузке страницы
if (window.location.search) {
    prefillFormFromUrl();
}
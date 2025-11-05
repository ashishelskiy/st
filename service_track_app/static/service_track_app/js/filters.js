let filterCounter = 1;

// Добавление нового фильтра
function addFilter() {
    console.log('✅ addFilter вызвана');
    filterCounter++;
    const filtersContainer = document.getElementById('filtersContainer');

    const newFilter = document.createElement('div');
    newFilter.className = 'filter-row';
    newFilter.innerHTML = `
        <select class="filter-field" name="filterField">
            <option value="status">Статус</option>
            <option value="dealer">Дилер</option>
            <option value="model">Модель</option>
            <option value="serial">Серийный номер</option>
            <option value="date">Дата создания</option>
        </select>
        <select class="filter-operator" name="filterOperator">
            <option value="equals">равно</option>
            <option value="contains">содержит</option>
            <option value="startswith">начинается с</option>
        </select>
        <input type="text" class="filter-value" placeholder="Значение">
        <button type="button" class="add-filter-btn" title="Добавить фильтр">➕</button>
        <button type="button" class="remove-filter-btn" title="Удалить фильтр">🗑️</button>
    `;

    filtersContainer.appendChild(newFilter);
    console.log('✅ Новый фильтр добавлен');
}

// Удаление фильтра
function removeFilter(button) {
    console.log('✅ removeFilter вызвана');
    const filterRow = button.closest('.filter-row');
    if (document.querySelectorAll('.filter-row').length > 1) {
        filterRow.remove();
        console.log('✅ Фильтр удален');
    }
}

// Применение всех фильтров
function applyAllFilters() {
    console.log('✅ applyAllFilters вызвана');
    const filterRows = document.querySelectorAll('.filter-row');
    const filters = [];

    filterRows.forEach(row => {
        const field = row.querySelector('.filter-field').value;
        const operator = row.querySelector('.filter-operator').value;
        const value = row.querySelector('.filter-value').value.trim();

        if (value) {
            filters.push({ field, operator, value });
        }
    });

    console.log('📋 Применяемые фильтры:', filters);

    if (filters.length === 0) {
        alert('⚠️ Заполните хотя бы один фильтр');
        return;
    }

    applyAdvancedFilter(filters);
}

// Очистка всех фильтров
function clearAllFilters() {
    console.log('✅ clearAllFilters вызвана');
    const filterRows = document.querySelectorAll('.filter-row');

    filterRows.forEach((row, index) => {
        row.querySelector('.filter-value').value = '';
        if (index > 0) {
            row.remove();
        }
    });

    filterCounter = 1;

    // Показываем все строки
    document.querySelectorAll('#requestsView tbody tr, .package-requests-mini-table tbody tr').forEach(row => {
        row.style.display = '';
    });

    console.log('✅ Все фильтры сброшены');
    alert('Фильтры сброшены!');
}

// Обновленная функция применения фильтров
function applyAdvancedFilter(filters) {
    console.log('🔍 applyAdvancedFilter вызвана');
    let rows = document.querySelectorAll('#requestsView tbody tr, .package-requests-mini-table tbody tr');
    console.log(`Найдено строк: ${rows.length}`);

    let visibleCount = 0;

    rows.forEach((row, index) => {
        let shouldDisplay = true;

        filters.forEach(filter => {
            if (!shouldDisplay) return;

            let cellValue = '';

            // Определяем значение ячейки в зависимости от поля
            switch(filter.field) {
                case 'status':
                    cellValue = row.cells[5]?.textContent.toLowerCase() || '';
                    break;
                case 'dealer':
                    cellValue = row.cells[4]?.textContent.toLowerCase() || '';
                    break;
                case 'model':
                    cellValue = row.cells[2]?.textContent.toLowerCase() || '';
                    break;
                case 'serial':
                    cellValue = row.cells[1]?.textContent.toLowerCase() || '';
                    break;
                case 'date':
                    cellValue = row.cells[7]?.textContent.toLowerCase() || '';
                    break;
            }

            console.log(`Строка ${index}: поле=${filter.field}, значение="${cellValue}", фильтр="${filter.value}"`);

            // Применяем оператор фильтрации
            switch(filter.operator) {
                case 'equals':
                    shouldDisplay = cellValue === filter.value.toLowerCase();
                    break;
                case 'contains':
                    shouldDisplay = cellValue.includes(filter.value.toLowerCase());
                    break;
                case 'startswith':
                    shouldDisplay = cellValue.startsWith(filter.value.toLowerCase());
                    break;
                case 'endswith':
                    shouldDisplay = cellValue.endsWith(filter.value.toLowerCase());
                    break;
            }
        });

        row.style.display = shouldDisplay ? '' : 'none';
        if (shouldDisplay) visibleCount++;
    });

    console.log(`✅ Отображено строк: ${visibleCount} из ${rows.length}`);
    alert(`Найдено записей: ${visibleCount}`);
}

// Делегирование событий
document.addEventListener('click', function(e) {
    // Кнопка добавления фильтра
    if (e.target.classList.contains('add-filter-btn')) {
        addFilter();
    }

    // Кнопка удаления фильтра
    if (e.target.classList.contains('remove-filter-btn')) {
        removeFilter(e.target);
    }

    // Кнопка применения фильтров
    if (e.target.classList.contains('apply-filters-btn')) {
        applyAllFilters();
    }

    // Кнопка сброса фильтров
    if (e.target.classList.contains('clear-filters-btn')) {
        clearAllFilters();
    }
});

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Filters JS загружен!');
    console.log('add-filter-btn:', document.querySelector('.add-filter-btn'));
    console.log('apply-filters-btn:', document.querySelector('.apply-filters-btn'));
    console.log('clear-filters-btn:', document.querySelector('.clear-filters-btn'));
});
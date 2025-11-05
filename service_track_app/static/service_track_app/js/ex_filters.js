let filterCounter = 1;

// Добавление нового фильтра
function addFilter() {
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
        <button type="button" class="add-filter-btn" onclick="addFilter()" title="Добавить фильтр">➕</button>
        <button type="button" class="remove-filter-btn" onclick="removeFilter(this)" title="Удалить фильтр">🗑️</button>
    `;

    filtersContainer.appendChild(newFilter);
}

// Удаление фильтра
function removeFilter(button) {
    const filterRow = button.closest('.filter-row');
    if (document.querySelectorAll('.filter-row').length > 1) {
        filterRow.remove();
    }
}

// Применение всех фильтров
function applyAllFilters() {
    const filterRows = document.querySelectorAll('.filter-row');
    const filters = [];

    filterRows.forEach(row => {
        const field = row.querySelector('.filter-field').value;
        const operator = row.querySelector('.filter-operator').value;
        const value = row.querySelector('.filter-value').value.trim();

        if (value) { // Добавляем только фильтры с заполненным значением
            filters.push({ field, operator, value });
        }
    });

    console.log('Применяемые фильтры:', filters);
    applyAdvancedFilter(filters);
}

// Очистка всех фильтров
function clearAllFilters() {
    const filterRows = document.querySelectorAll('.filter-row');

    // Очищаем значения всех фильтров кроме первого
    filterRows.forEach((row, index) => {
        row.querySelector('.filter-value').value = '';
        if (index > 0) {
            row.remove();
        }
    });

    filterCounter = 1;
    clearAdvancedFilter();
}

// Обновленная функция применения фильтров
function applyAdvancedFilter(filters) {
    let rows = document.querySelectorAll('#requestsView tbody tr, .package-requests-mini-table tbody tr');

    rows.forEach(row => {
        let shouldDisplay = true;

        filters.forEach(filter => {
            if (!shouldDisplay) return; // Если уже не должен отображаться, пропускаем

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
    });
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчики для кнопок
    document.querySelector('.apply-filters-btn').addEventListener('click', applyAllFilters);
    document.querySelector('.clear-filters-btn').addEventListener('click', clearAllFilters);

    // Добавляем обработчик для первой кнопки добавления
    document.querySelector('.add-filter-btn').addEventListener('click', addFilter);
});
document.addEventListener('DOMContentLoaded', () => {
    const taskBtn = document.getElementById('task9Btn');
    const contentArea = document.querySelector('.content-area');

    if (!taskBtn || !contentArea) return;

    taskBtn.addEventListener('click', () => {
        document.querySelectorAll('.task-btn').forEach(btn => btn.classList.remove('active'));
        taskBtn.classList.add('active');

        contentArea.innerHTML = `
            <div style="max-width: 500px; margin: 0 auto; padding: 30px; background: #f8f9fa; border-radius: 16px; border: 1px solid #ddd; text-align: center;">
                <h3 style="margin-top: 0; color: #333;">Вибір дати</h3>
                <p style="color: #666; margin-bottom: 30px;">
                    Клікніть на поле, щоб відкрити візуальний календар
                </p>

                <label for="dateInput" style="display: block; margin-bottom: 12px; font-weight: bold; font-size: 1.2rem;">
                    Обрана дата:
                </label>
                
                <input type="text" 
                       id="dateInput" 
                       readonly 
                       placeholder="ДД.ММ.РРРР" 
                       style="padding: 14px 20px; 
                              width: 280px; 
                              border: 1px solid #ccc; 
                              border-radius: 50px; 
                              font-size: 1.1rem; 
                              background: #fff; 
                              cursor: pointer; 
                              text-align: center;">

                <div id="datepicker" style="
                    display: none;
                    position: absolute;
                    background: white;
                    border: 1px solid #ccc;
                    border-radius: 16px;
                    padding: 20px;
                    margin-top: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    z-index: 1000;
                    width: 340px;
                    left: 50%;
                    transform: translateX(-50%);
                ">
                </div>
            </div>
        `;

        initDatepicker();
    });

    function initDatepicker() {
        const dateInput = document.getElementById('dateInput');
        const datepicker = document.getElementById('datepicker');
        let currentDate = new Date();
        let selectedDate = null;

        dateInput.addEventListener('click', (e) => {
            e.stopPropagation();
            datepicker.style.display = 'block';
            renderCalendar(currentDate);
        });

        document.addEventListener('click', (e) => {
            if (!dateInput.contains(e.target) && !datepicker.contains(e.target)) {
                datepicker.style.display = 'none';
            }
        });

        datepicker.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        function renderCalendar(date) {
            datepicker.innerHTML = '';

            const header = document.createElement('div');
            header.style.display = 'flex';
            header.style.justifyContent = 'space-between';
            header.style.alignItems = 'center';
            header.style.marginBottom = '20px';
            header.style.fontSize = '1.4rem';
            header.style.fontWeight = 'bold';

            const prevBtn = document.createElement('button');
            prevBtn.textContent = '‹';
            prevBtn.style.background = 'none';
            prevBtn.style.border = 'none';
            prevBtn.style.fontSize = '28px';
            prevBtn.style.cursor = 'pointer';
            prevBtn.onclick = (e) => {
                e.stopPropagation();
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar(currentDate);
            };

            const title = document.createElement('div');
            const months = ['Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
                'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'];
            title.textContent = `${months[date.getMonth()]} ${date.getFullYear()}`;

            const nextBtn = document.createElement('button');
            nextBtn.textContent = '›';
            nextBtn.style.background = 'none';
            nextBtn.style.border = 'none';
            nextBtn.style.fontSize = '28px';
            nextBtn.style.cursor = 'pointer';
            nextBtn.onclick = (e) => {
                e.stopPropagation();
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar(currentDate);
            };

            header.appendChild(prevBtn);
            header.appendChild(title);
            header.appendChild(nextBtn);
            datepicker.appendChild(header);

            const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'];
            const grid = document.createElement('div');
            grid.style.display = 'grid';
            grid.style.gridTemplateColumns = 'repeat(7, 1fr)';
            grid.style.gap = '10px';
            grid.style.textAlign = 'center';
            grid.style.maxWidth = '100%';

            weekdays.forEach(day => {
                const el = document.createElement('div');
                el.textContent = day;
                el.style.fontWeight = 'bold';
                el.style.color = '#444';
                el.style.padding = '8px 0';
                grid.appendChild(el);
            });

            const year = date.getFullYear();
            const month = date.getMonth();
            const firstDayOfMonth = new Date(year, month, 1);
            const dayOfWeek = firstDayOfMonth.getDay();

            const startOffset = dayOfWeek === 0 ? 6 : dayOfWeek - 1;

            for (let i = 0; i < startOffset; i++) {
                const empty = document.createElement('div');
                grid.appendChild(empty);
            }

            const daysInMonth = new Date(year, month + 1, 0).getDate();
            for (let day = 1; day <= daysInMonth; day++) {
                const dayEl = document.createElement('div');
                dayEl.textContent = day;
                dayEl.style.padding = '12px';
                dayEl.style.cursor = 'pointer';
                dayEl.style.borderRadius = '50%';
                dayEl.style.transition = 'all 0.2s';
                dayEl.style.fontSize = '1.1rem';

                dayEl.onmouseover = () => dayEl.style.background = '#e3f2fd';
                dayEl.onmouseout = () => {
                    if (!dayEl.classList.contains('selected')) dayEl.style.background = '';
                };

                dayEl.onclick = (e) => {
                    e.stopPropagation();
                    selectedDate = new Date(year, month, day);
                    dateInput.value = selectedDate.toLocaleDateString('uk-UA', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric'
                    });
                    datepicker.style.display = 'none';
                };

                if (selectedDate && selectedDate.getDate() === day &&
                    selectedDate.getMonth() === month &&
                    selectedDate.getFullYear() === year) {
                    dayEl.style.background = '#007bff';
                    dayEl.style.color = 'white';
                    dayEl.classList.add('selected');
                }

                grid.appendChild(dayEl);
            }

            datepicker.appendChild(grid);

            const controls = document.createElement('div');
            controls.style.display = 'flex';
            controls.style.justifyContent = 'space-between';
            controls.style.gap = '12px';
            controls.style.marginTop = '15px';

            const todayBtn = document.createElement('button');
            todayBtn.textContent = 'Сьогодні';
            todayBtn.style.flex = '1';
            todayBtn.style.padding = '12px';
            todayBtn.style.background = '#28a745';
            todayBtn.style.color = 'white';
            todayBtn.style.border = 'none';
            todayBtn.style.borderRadius = '50px';
            todayBtn.style.cursor = 'pointer';
            todayBtn.onclick = (e) => {
                e.stopPropagation();
                currentDate = new Date();
                selectedDate = new Date();
                dateInput.value = selectedDate.toLocaleDateString('uk-UA', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
                renderCalendar(currentDate);
            };

            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'Відмінити';
            cancelBtn.style.flex = '1';
            cancelBtn.style.padding = '12px';
            cancelBtn.style.background = '#dc3545';
            cancelBtn.style.color = 'white';
            cancelBtn.style.border = 'none';
            cancelBtn.style.borderRadius = '50px';
            cancelBtn.style.cursor = 'pointer';
            cancelBtn.onclick = (e) => {
                e.stopPropagation();
                dateInput.value = '';
                selectedDate = null;
                datepicker.style.display = 'none';
            };

            controls.appendChild(todayBtn);
            controls.appendChild(cancelBtn);
            datepicker.appendChild(controls);
        }
    }
});
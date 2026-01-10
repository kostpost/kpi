let userSelectedDate = null;
const startBtn = document.querySelector('[data-start]');
const datetimePicker = document.getElementById('datetime-picker');

flatpickr(datetimePicker, {
    enableTime: true,
    time_24hr: true,
    defaultDate: new Date(),
    minuteIncrement: 1,
    onClose(selectedDates) {
        userSelectedDate = selectedDates[0];

        if (userSelectedDate <= new Date()) {
            iziToast.error({
                title: 'Помилка',
                message: 'Оберіть дату в майбутньому',
                position: 'topRight',
                timeout: 4000
            });
            startBtn.disabled = true;
        } else {
            startBtn.disabled = false;
        }
    },
});

function addLeadingZero(value) {
    return String(value).padStart(2, '0');
}

function convertMs(ms) {
    const second = 1000;
    const minute = second * 60;
    const hour = minute * 60;
    const day = hour * 24;

    const days = Math.floor(ms / day);
    const hours = Math.floor((ms % day) / hour);
    const minutes = Math.floor(((ms % day) % hour) / minute);
    const seconds = Math.floor((((ms % day) % hour) % minute) / second);

    return { days, hours, minutes, seconds };
}

function updateTimer({ days, hours, minutes, seconds }) {
    document.querySelector('[data-days]').textContent = addLeadingZero(days);
    document.querySelector('[data-hours]').textContent = addLeadingZero(hours);
    document.querySelector('[data-minutes]').textContent = addLeadingZero(minutes);
    document.querySelector('[data-seconds]').textContent = addLeadingZero(seconds);
}

startBtn.addEventListener('click', () => {
    if (!userSelectedDate) return;

    startBtn.disabled = true;
    datetimePicker.disabled = true;

    const timerId = setInterval(() => {
        const timeLeft = userSelectedDate - new Date();

        if (timeLeft <= 0) {
            clearInterval(timerId);
            updateTimer({ days: 0, hours: 0, minutes: 0, seconds: 0 });
            datetimePicker.disabled = false;
            return;
        }

        const time = convertMs(timeLeft);
        updateTimer(time);
    }, 1000);
});
(function() {
    window.sortDates = function(dates) {
        const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

        const splitTimeString = (timeString) => {
            const [day, time, period] = timeString.split(' ');
            const [hour, minute] = time.split(':').map(Number);
            return { day, hour, minute, period };
        };
        if (typeof dates === 'string') {
        dates = dates.split(',')
        }
        dates.sort((a, b) => {
            const { day: dayA, hour: hourA, minute: minuteA, period: periodA } = splitTimeString(a);
            const { day: dayB, hour: hourB, minute: minuteB, period: periodB } = splitTimeString(b);

            const totalMinutesA = (dayOrder.indexOf(dayA) * 24 * 60) +
                                  ((periodA === "PM" && hourA !== 12 ? hourA + 12 : (periodA === "AM" && hourA === 12 ? 0 : hourA)) * 60) +
                                  minuteA;
            const totalMinutesB = (dayOrder.indexOf(dayB) * 24 * 60) +
                                  ((periodB === "PM" && hourB !== 12 ? hourB + 12 : (periodB === "AM" && hourB === 12 ? 0 : hourB)) * 60) +
                                  minuteB;

            return totalMinutesA - totalMinutesB;
        });
    };
})();

function getStartTimer() {
    let dateTimeString = $('#timer_start_date').val();
    let formattedDateString = dateTimeString.replace(" ", "T");
    let dateObject = new Date(formattedDateString + 'Z');
    return dateObject.getTime();
}

function getPauseTimer() {
    let dateTimeString = $('#timer_pause_date').val();
    let formattedDateString = dateTimeString.replace(" ", "T");
    let dateObject = new Date(formattedDateString + 'Z');
    return dateObject.getTime();
}

class TimerService {
    constructor() {
        this.offset = 0;
        this.timer = null;
        this.timerFormatted = "";
        this.startTime = null;
        this.pauseTime = null;
        this.elapsedTime = 0;
    }

    computeOffset(serverTime) {
        const currentTime = new Date().getTime();
        this.offset = currentTime - serverTime;
    }

    getCurrentTime(time) {
        return new Date().getTime() - this.offset;
    }

    startTimer(startTime) {
        this.startTime = startTime;
        this.elapsedTime = 0;
        this.updateTimer();
    }

    pauseTimer(pause_date) {
        this.pauseTime = pause_date;
        this.elapsedTime += this.pauseTime - this.startTime;
        clearInterval(this.timer);
    }

    resumeTimer(pause_time) {
        const serverTime = new Date().getTime(); // Simulate getting server time
        let milliseconds = getStartTimer()
        this.startTime = milliseconds + (serverTime - pause_time);
        this.updateTimer();
    }

    stopTimer() {
        clearInterval(this.timer);
        this.timerFormatted = "";
        this.startTime = null;
        this.pauseTime = null;
        this.elapsedTime = 0;
    }

    updateTimer() {
        this.timer = setInterval(() => {
            const currentTime = this.getCurrentTime();
            const elapsed = (currentTime - this.startTime + this.elapsedTime) / 1000;
            this.timerFormatted = this.formatTime(elapsed);
        }, 1000);
    }

    formatTime(seconds) {
        const hrs = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const mins = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
        return `${hrs}:${mins}:${secs}`;
    }
}

class TimerComponent {
    constructor(timerService) {
        this.timerService = timerService;
        this.state = {
            startDate: null,
            pauseDate: null,
        };
    }

    onStart() {
        const serverTime = new Date().getTime(); // Simulate getting server time
        let start_timer_start = getStartTimer()
        this.state.startDate = new Date(start_timer_start).toLocaleString();
        this.timerService.startTimer(start_timer_start);
        this.updateUI(this.timerService.timerFormatted);
        this.timerService.timer = setInterval(() => {
            this.updateUI(this.timerService.timerFormatted);
        }, 1000);
    }

    onPause() {
        let pause_date = getPauseTimer()
        this.state.pauseDate = new Date(pause_date).toLocaleString();
        this.timerService.pauseTimer(pause_date);
        this.updateUI(this.timerService.timerFormatted);
    }

    onResume() {
        let pause_time = this.state.pauseDate
        this.state.pauseDate = null;
        this.timerService.resumeTimer(pause_time);
        this.updateUI(this.timerService.timerFormatted);
    }

    onStop() {
        this.timerService.stopTimer();
        this.state.startDate = null;
        this.state.pauseDate = null;
        this.updateUI("");
    }

    updateUI(time) {
        if (time) {
            document.getElementById('timer-display').innerText = time;
        }
    }
}

const timerService = new TimerService();
const timerComponent = new TimerComponent(timerService);
let timer_start_date = $('#timer_start_date').val()
let timer_pause_date = $('#timer_pause_date').val()
let is_timer_running = $('#is_timer_running').val()
if (timer_start_date && is_timer_running && !timer_pause_date) {
    timerComponent.onStart();
}
if (timer_start_date && !is_timer_running && timer_pause_date) {
    timerComponent.onPause();
}
if (!timer_start_date) {
    timerComponent.onStop()
}
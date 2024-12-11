function addHalvingTime(data) {
    const halvingTime = data.halving_time;
    document.getElementById('mean_halving_time').textContent = data.halving_time.toFixed(1);
    }

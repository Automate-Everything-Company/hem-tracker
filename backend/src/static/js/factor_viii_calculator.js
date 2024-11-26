function calculatePeakLevel() {
    const dosage = document.getElementById('dosage').value;
    const weight = document.getElementById('weight').value;

    if (dosage && weight) {
        const peakLevel = (dosage / (weight * 0.5)).toFixed(0);
        document.getElementById('resultValue').value = peakLevel;
    } else {
        alert("Please enter both the dosage and weight.");
    }
}

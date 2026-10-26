// main_app/static/main_app/js/roulette.js

const rouletteWheel = document.getElementById('rouletteWheel');
const rouletteResult = document.getElementById('rouletteResult');
const rouletteSpinBtn = document.getElementById('rouletteSpinBtn');
const rouletteSectors = [];

function buildRouletteSectors() {
    const count = 20;
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(i % 2 === 0 ? '#c8102e' : '#14141a');
    }
    const step = 360 / count;
    const stops = [];
    for (let i = 0; i < count; i++) {
        stops.push(`${colors[i]} ${(i * step).toFixed(2)}deg ${((i + 1) * step).toFixed(2)}deg`);
    }
    rouletteWheel.style.background = `conic-gradient(${stops.join(', ')})`;
    rouletteSectors.length = 0;
    rouletteSectors.push(...colors);
}

buildRouletteSectors();

rouletteSpinBtn.addEventListener('click', () => {
    const step = 360 / rouletteSectors.length;
    const winIndex = Math.floor(Math.random() * rouletteSectors.length);
    const winColor = rouletteSectors[winIndex];
    const targetAngle = -(winIndex * step + step / 2);

    rouletteWheel.style.transition = 'transform 4s cubic-bezier(0.12, 0.8, 0.08, 1)';
    rouletteWheel.style.transform = `rotate(${targetAngle}deg)`;
    rouletteSpinBtn.disabled = true;

    rouletteWheel.addEventListener('transitionend', function handler(e) {
        if (e.propertyName !== 'transform') return;
        rouletteWheel.removeEventListener('transitionend', handler);
        rouletteSpinBtn.disabled = false;
        const isRed = winColor === '#c8102e';
        rouletteResult.innerText = isRed ? 'КРАСНОЕ' : 'ЧЁРНОЕ';
        rouletteResult.className = 'roulette-result ' + (isRed ? 'red' : 'black');
        if (isRed) {
            rouletteResult.innerText = 'КРАСНОЕ! СЛАВА ПОЛИТЕХУ!';
        } else {
            rouletteResult.innerText = 'ЧЁРНОЕ... Увы, баланс ушел Политеху. Зато это точно не штурм!';
        }
    }, { once: true });
});

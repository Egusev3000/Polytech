// main_app/static/main_app/js/casino.js

const items = ['seven', 'cherry', 'lemon', 'diamond', 'polytech', 'bar'];
const labelMap = {
    'seven': '777', 'cherry': 'CHERRY', 'lemon': 'LEMON',
    'diamond': 'DIAMOND', 'polytech': 'POLY', 'bar': 'BAR'
};

let balance = typeof initialBalance !== 'undefined' ? initialBalance : 1000;
let currentBet = 50;

document.addEventListener("DOMContentLoaded", function() {
    const spinBtn = document.getElementById('spin-btn');
    const dogText = document.getElementById('dog-text');
    const slotWrapper = document.querySelector('.casino-wrapper');
    const dogContainer = document.querySelector('.slop-dog-container');
    const betInput = document.getElementById('bet-input');

    window.adjustBet = function(val) {
        if (spinBtn.disabled) return;
        currentBet = parseInt(betInput.value) + val;
        restrictBetValues();
    };

    window.setAllIn = function() {
        if (spinBtn.disabled) return;
        currentBet = balance;
        restrictBetValues();
        playSound(500, 'sawtooth', 0.1);
    };

    window.validateBetInput = function(input) {
        currentBet = parseInt(input.value) || 50;
        restrictBetValues();
    };

    function restrictBetValues() {
        if (currentBet < 1) currentBet = 1;
        if (currentBet > balance) currentBet = balance;
        if (currentBet > 1000) currentBet = 1000;
        betInput.value = currentBet;
    }

    window.spinSlots = function() {
        currentBet = parseInt(betInput.value) || 50;
        restrictBetValues();

        if (balance < currentBet || balance <= 0) {
            alert("Недостаточно ВПК! Пополните счет фейковой картой в Личном Кабинете!");
            return;
        }

        slotWrapper.classList.remove('win-flash');
        dogContainer.classList.remove('dog-jump');

        for(let r=0; r<3; r++) {
            for(let c=0; c<5; c++) {
                const cell = document.getElementById(`cell-${r}-${c}`);
                if (cell) cell.classList.remove('winning-cell');
            }
        }

        spinBtn.disabled = true;
        betInput.disabled = true;

        fetch('/casino/action/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({action: 'spin', bet: currentBet})
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                balance = data.balance;
                document.getElementById('balance-val').innerText = balance;
                runMatrixAnimation();
            } else {
                spinBtn.disabled = false;
                betInput.disabled = false;
                alert(data.error);
            }
        })
        .catch(() => {
            spinBtn.disabled = false;
            betInput.disabled = false;
        });
    };

    function runMatrixAnimation() {
        dogText.innerText = "Рендеринг... Шансы урезаны до минимума по совету Минцифры.";
        let count = 0;

        let interval = setInterval(() => {
            for(let row=0; row<3; row++) {
                for(let col=0; col<5; col++) {
                    const cell = document.getElementById(`cell-${row}-${col}`);
                    if (cell) {
                        const randomItem = items[Math.floor(Math.random() * items.length)];
                        cell.className = 'reel-slot ' + randomItem;
                        cell.innerText = labelMap[randomItem];
                    }
                }
            }
            playSound(180 + (count * 25), 'square', 0.04);
            count++;

            if(count > 15) {
                clearInterval(interval);
                evaluateMatrixResults();
            }
        }, 75);
    }

    function evaluateMatrixResults() {
        // МАТЕМАТИЧЕСКИЙ РЕЗАХ ШАНСОВ (92% шанс мгновенного слива на этапе вычислений)
        let rigFactor = Math.random();

        let matrix = [];
        for(let row=0; row<3; row++) {
            matrix[row] = [];
            for(let col=0; col<5; col++) {
                const cell = document.getElementById(`cell-${row}-${col}`);
                const cellClass = cell ? cell.className : '';
                matrix[row][col] = cellClass.replace('reel-slot ', '');
            }
        }

        let specialCount = 0;
        for(let r=0; r<3; r++) {
            for(let c=0; c<5; c++) {
                if(matrix[r][c] === 'seven') specialCount++;
            }
        }

        let isSmallWin = (matrix[1][0] === matrix[1][1] && matrix[1][1] === matrix[1][2]);

        // Выигрыш сработает ТОЛЬКО если пройдена жесткая проверка рандома казино
        if (specialCount >= 7 && rigFactor > 0.995) {
            sendWinToServer('maxwin', null);
        } else if (isSmallWin && rigFactor > 0.85) {
            sendWinToServer('small', 1);
        } else {
            // Искусственно превращаем совпадения в проигрыш, если рандомайзер против игрока
            document.getElementById('casino-result').innerText = "Ряд не совпал. Повезет на пересдаче! 🔥";
            dogText.innerText = "Увы, баланс ушел Политеху. Зато это точно не штурм!";
            playSound(120, 'triangle', 0.3);
            spinBtn.disabled = false;
            betInput.disabled = false;
        }
    }

    function sendWinToServer(type, winningRow) {
        fetch('/casino/action/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({action: 'win', type: type, bet: currentBet})
        })
        .then(res => res.json())
        .then(data => {
            balance = data.balance;
            document.getElementById('balance-val').innerText = balance;
            document.getElementById('win-val').innerText = data.prize;

            slotWrapper.classList.add('win-flash');
            dogContainer.classList.add('dog-jump');

            if(type === 'maxwin') {
                document.getElementById('casino-result').innerHTML = `<span style='color: #ff00ff; font-size:26px;'>⚡ МАКС ВИН (х20)!!! +${data.prize} ВПК!!! ⚡</span>`;
                dogText.innerText = "ЧТО?! Вы пробили 0.5% шанс! Нейрособака Hailuo AI лает от шока!";

                for(let r=0; r<3; r++) {
                    for(let c=0; c<5; c++) {
                        const cell = document.getElementById(`cell-${r}-${c}`);
                        if (cell) cell.classList.add('winning-cell');
                    }
                }
            } else {
                document.getElementById('casino-result').innerHTML = `<span style='color: #00ff00;'>Утешительный приз: +${data.prize} ВПК (х0.5)</span>`;
                dogText.innerText = "Частичный возврат ставки! Попробуй All In во славу Политеха!";

                for(let c=0; c<5; c++) {
                    const cell = document.getElementById(`cell-${winningRow}-${c}`);
                    if (cell) cell.classList.add('winning-cell');
                }
            }
            spinBtn.disabled = false;
            betInput.disabled = false;
        });
    }
});

function playSound(freq, type, duration) {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + duration);
        osc.stop(ctx.currentTime + duration);
    } catch(e) {}
}

var size = 640;
var n = 64;
var game = [];
var currTurn = 0;
var autoTimer;

function drawGrid(ctx) {
    let b = size / n;
    ctx.strokeStyle = 'rgba(60, 60, 60, 0.5)';
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    for(var i = 0; i <= n; i++) {
        ctx.moveTo(0, i*b);
        ctx.lineTo(size - 1, i*b);
        ctx.moveTo(i*b, 0);
        ctx.lineTo(i*b, size - 1);
    }
    ctx.stroke();
}

function drawUnit(ctx, i, j, player) {
    let b = size / n;
    let playerCol = ['255, 0, 0', '0, 255, 0', '0, 0, 255', '0, 140, 140'];
    ctx.fillStyle = 'rgba(' + playerCol[player] + ', 0.7)';
    ctx.fillRect(i*b + 1, j*b + 1, b - 2, b - 2);
}

function drawPoint(ctx, i, j) {
    let b = size / n;
    ctx.fillStyle = 'rgba(200, 200, 0, 0.5)';
    ctx.fillRect(i*b + 1, j*b + 1, b - 2, b - 2);    
}

async function loadGame(uri) {
    let response = await fetch(uri);
    let data = await response.text();
    let json = '[' + data.replace(/\n/g, "\n,").replace(/'/g, "\"").replace(/True/g, "true").replace(/False/g, "false").replace(/\(/g, '[').replace(/\)/g, ']').slice(0, -2) + ']';
    return await JSON.parse(json);
}

function drawState(turn) {
    var canvas = document.getElementById("world");
    var ctx = canvas.getContext("2d");
    document.getElementById("currTurn").innerHTML = "Current turn: " + turn;
    
    state = game[turn];
    
    ctx.clearRect(0, 0, size, size);
    drawGrid(ctx);
    
    for(const [i, bot] of state.bots.entries()) {
        drawUnit(ctx, bot.pos[0], bot.pos[1], i);
    }

    for(const point of state.points) {
        drawPoint(ctx, point[0], point[1]);
    }

    let playerCol = ['255, 0, 0', '0, 255, 0', '0, 0, 255', '0, 140, 140'];

    var energies = document.getElementById("energies");
    var statTable = "<table><tr><th>Player</th><th>Score</th><th>Energy</th><th>Debug</th></tr>"
    for(const [i, bot] of state.bots.entries()) {
        let col = "rgba(" + playerCol[i] + ", 0.1)"
        statTable += "<tr style=\"background-color:" + col + ";\"><td>" + i + "</td><td>" + bot.points + "</td><td>" + bot.energy + "</td><td>" + bot.debug + "</td></tr>"
    }
    statTable += "</table>"
    energies.innerHTML = statTable;
}

async function init() {
    var canvas = document.getElementById("world");
    var ctx = canvas.getContext("2d");

    size = canvas.width;
    currTurn = 0;
    
    game = await loadGame('/log.txt');
    drawState(currTurn);
}

async function drawNext() {
    if(currTurn < game.length - 1) {
        currTurn++;
        drawState(currTurn);
    }
}

async function drawPrev() {
    if(currTurn > 0) {
        currTurn--;
        drawState(currTurn);
    }
}

function startAuto() {
    autoTimer = setInterval(drawNext, 250);
}

function gotoStart() {
    currTurn = 0;
    drawState(currTurn);
}

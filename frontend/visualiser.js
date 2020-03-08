var size = 640;
var n = 64;
var game = [];
var board = [];
var meta = {};
var currTurn = 0;
var autoTimer;
let playerCol = ['71, 50, 102', '33, 209, 25', '255, 0, 0', '0, 255, 255', '255, 0, 255', '127, 0, 0', '255, 127, 0', '0, 127, 0'];

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

    for(var i = 0; i < n; i++)
        for(var j = 0; j < n; j++)
            if(board[i][j] == '#')
                drawWall(ctx, i, j);
}

function drawUnit(ctx, j, i, player) {
    let b = size / n;
    ctx.fillStyle = 'rgba(' + playerCol[player] + ', 0.7)';
    ctx.fillRect(i*b + 1, j*b + 1, b - 2, b - 2);
}

function drawPoint(ctx, j, i) {
    let b = size / n;
    ctx.fillStyle = 'rgba(200, 200, 0, 0.5)';
    ctx.fillRect(i*b + 1, j*b + 1, b - 2, b - 2);    
}

function drawWall(ctx, j, i) {
    let b = size / n;
    ctx.fillStyle = 'rgba(60, 60, 60, 0.7)';
    ctx.fillRect(i*b + 1, j*b + 1, b - 2, b - 2);    
}

async function parseGame(data) {
    let json = data.replace(/\n/g, "").replace(/'/g, "\"").replace(/True/g, "true").replace(/False/g, "false").replace(/\(/g, '[').replace(/\)/g, ']');
    return await JSON.parse(json);
}

async function loadGame(uri) {
    let response = await fetch(uri, {cache: "reload"});
    let data = await response.text();
    return await parseGame(data);
}

function friendlyName(name) {
    name = name.replace("programs/", "").replace(".A.bin", "").replace(".B.bin", "").replace(".C.bin", "");
    if(/^player[1-8]$/.exec(name)) {
        players = ["EJOI ekipica", "Infinity", "Inspekcija", "Robot 4", "Robot 5", "Robot 6", "Robot 7", "Robot 8"];
        name = players[name.substr(6) - 1];
    }
    return name;
}

function drawState(turn) {
    var canvas = document.getElementById("world");
    var ctx = canvas.getContext("2d");
    document.getElementById("currTurn").innerHTML = "Trenutni potez: " + turn;
    
    state = game[turn];
    
    ctx.clearRect(0, 0, size, size);
    drawGrid(ctx);
    
    for(const [i, bot] of state.bots.entries()) {
        drawUnit(ctx, bot.pos[0], bot.pos[1], i);
    }

    for(const point of state.points) {
        drawPoint(ctx, point[0], point[1]);
    }



    var energies = document.getElementById("energies");
    var statTable = "<table><tr><th>Robot</th><th>Poeni</th><th>Energija</th><th>Debug</th></tr>"
    for(const [i, bot] of state.bots.entries()) {
        let col = "rgba(" + playerCol[i] + ", 0.1)"
        let energy = bot.energy;
        if(!bot.alive)
            energy = "&mdash;"
        botName = friendlyName(meta.players[i]);
        statTable += "<tr style=\"background-color:" + col + ";\"><td>" + botName + "</td><td>" + bot.points + "</td><td>" + energy + "</td><td>" + bot.debug + "</td></tr>"
    }
    statTable += "</table>"
    energies.innerHTML = statTable;
}

async function init() {
    var canvas = document.getElementById("world");
    var ctx = canvas.getContext("2d");

    size = canvas.width;
    currTurn = 0;

    game = window.location.search.substr(1);
    ok = /^[a-zA-Z0-9_.]+$/
    if(!ok.exec(game))
        game = "";
    else
        game = "logs/" + game;

    if(game) {
        data = await loadGame(game);
        game = data.turns;
        board = data.board;
        meta = data.meta;
    }
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
    clearInterval(autoTimer);
    autoTimer = setInterval(drawNext, 250);
}

function gotoStart() {
    currTurn = 0;
    drawState(currTurn);
}

async function loadLocal() {
    var picker = document.getElementById("gameFile");
    console.log(picker.files.item(0));

    var reader = new FileReader();
    reader.onload = async function() {
        data = await parseGame(reader.result);
        game = data.turns;
        board = data.board;
        meta = data.meta;
    }

    reader.readAsText(picker.files.item(0));
    drawState(currTurn);
}

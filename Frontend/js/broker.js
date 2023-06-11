function updateBroker() {
    /*fetch(`http://127.0.0.1:5000/api/get-balance`, {
            method: "POST"})  
        .then(response => response.json())
        .then(balance => {
            document.getElementById("balance").innerHTML = `Balance: ${balance["balance"]}`;
    })*/

    fetch(`http://127.0.0.1:5000/api/get-equity`, {
            method: "POST"})  
        .then(response => response.json())
        .then(equity => {
            document.getElementById("equity").innerHTML = `Equity: ${equity["equity"]}`;
    })
    
    
    showOpenPositions();

}

updateBroker()

export { updateBroker };

function openPosition(type) {
    let positionForm = document.forms["position-form"];

    let pair =  "EURUSD" //positionForm["pair"].value;
    let tp = positionForm["tp"].value;
    let sl = positionForm["sl"].value;

    fetch(`http://127.0.0.1:5000/api/open-position?type=${type}&pair=${pair}&tp=${tp}&sl=${sl}`, {method: "POST"})
    .then(response => response.json())
    .then(status => {
        updateBroker();
    })
}

function showOpenPositions() {
    const openPositionsContainer = document.getElementById("open-positions");
    openPositionsContainer.innerHTML = "";
    const arrow = '\u2192'
    

    fetch("http://127.0.0.1:5000/api/fetch-open-positions", {method: "POST"})
    .then(response => response.json())
    .then(openPositions => {
        openPositions.forEach(position => {
            let openPositionContainer = document.createElement("div");
            openPositionContainer.className = "position";
            openPositionContainer.id = position["id"];

            let positionBalance = document.createElement("h4");
            positionBalance.className = "position-balance";

            let profitLoss = position["profit_loss"];
            positionBalance.innerHTML = `${Math.round(position["starting_size"] + profitLoss)}`;

            if (profitLoss >= 0) {
                positionBalance.style.cssText = "color: #2A32B9;";
            } else{
                positionBalance.style.cssText = "color: #EF5350;";
            }
            openPositionContainer.appendChild(positionBalance);

            let positionTarget = document.createElement("h5");
            positionTarget.className = "target";
            positionTarget.innerHTML = `${position["open_rate"]} ${arrow} ${position["tp"]}`;
            openPositionContainer.appendChild(positionTarget);
            
            

            let closePositionButton = document.createElement("button");
            closePositionButton.className = "close-position";
            closePositionButton.innerHTML = "Close";
            closePositionButton.addEventListener("click", function() {
                fetch(`http://127.0.0.1:5000/api/close-position?id=${position["id"]}`, {method: "POST"})
                .then(response => response.json())
                .then(status => {
                    updateBroker();
                })
            })

            openPositionContainer.appendChild(closePositionButton);

            openPositionsContainer.appendChild(openPositionContainer);
        });
        
    })
}


document.getElementById("long").addEventListener('click', function () {
    openPosition("long");
    
})

document.getElementById("short").addEventListener('click', function () {
    openPosition("short");
    
})
function updateBalance() {
    fetch(`http://127.0.0.1:5000/api/get-balance`, {
            method: "POST"})  
        .then(response => response.json())
        .then(balance => {
            document.getElementById("balance").innerHTML = `Balance: ${balance["balance"]}`;
    })  
}

updateBalance()

export { updateBalance };

function openPosition() {
    let positionForm = document.forms["position-form"];

    let type = positionForm["type"].value;
    let size = positionForm["size"].value;
    let pair = positionForm["pair"].value;
    let tp = positionForm["tp"].value;
    let sl = positionForm["sl"].value;

    fetch(`http://127.0.0.1:5000/api/open-position?type=${type}&size=${size}&pair=${pair}&tp=${tp}&sl=${sl}`, {
            method: "POST"})  
        .then(response => response.json())
        .then(meta => {
            console.log(meta)
    }) 
}


document.getElementById("open-position").addEventListener('click', function () {
    openPosition();
})
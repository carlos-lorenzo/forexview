import { createChart } from '/node_modules/lightweight-charts/dist/lightweight-charts.standalone.development.mjs';

document.getElementById("reset-time").addEventListener("click", function(){
    fetch("http://127.0.0.1:5000/api/reset-time", {
        method: "POST"})
    .then(function() {
        window.location.reload();
    })
})


function createCandleChart(timeFrame) {
    const chartContainer = document.getElementById(timeFrame)
    const chart = createChart(chartContainer, { width: 500, height: 500 });
    const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
        wickUpColor: '#26a69a', wickDownColor: '#ef5350', priceFormat: { type: 'price', precision: 5, minMove: 0.0001 }
    });

    chart.priceScale('right').applyOptions({
        ticksVisible: true,
    })

    candlestickSeries.applyOptions({
        
    })

    fetch(`http://127.0.0.1:5000/api/get-chart-data?tf=${timeFrame}`, {
        method: "POST"})
    .then(response => response.json())  
    .then(chartData => {
        candlestickSeries.setData(chartData);
        chart.timeScale().fitContent(); 
    })

    return {
        "chart": chart,
        "candle": candlestickSeries
    }
}


function setChartData(timeFrame, candlestickSeries){
    fetch(`http://127.0.0.1:5000/api/get-chart-data?tf=${timeFrame}`, {
        method: "POST"})
    .then(response => response.json())  
    .then(chartData => {
        candlestickSeries.setData(chartData);
    })
}

function updateChart(timeFrame,  candlestickSeries){
    fetch(`http://127.0.0.1:5000/api/new-candle?tf=${timeFrame}`, {
            method: "POST"})  
        .then(response => response.json())
        .then(newCandleData => {
            candlestickSeries.update(newCandleData);
    })
}


const timeFrames = ["1m", "15m", "4h", "1D"];
var charts = {};

var chartUpdates = [];

timeFrames.forEach(timeFrame => {
    charts[timeFrame] = createCandleChart(timeFrame);
    chartUpdates.push({
        "tf": timeFrame, 
        "button": document.getElementById(`${timeFrame}-new-candle`)
    });
})

chartUpdates.forEach(updateData => {

    let timeFrame = updateData["tf"]
    let button = updateData["button"]

    button.addEventListener('click', function () {

        fetch(`http://127.0.0.1:5000/api/update-time?tf=${timeFrame}`, {method: "GET"})
        
        for (let chartTimeFrame in charts) {

            let candlestickSeries = charts[chartTimeFrame]["candle"];

            if (chartTimeFrame == timeFrame) {
                updateChart(chartTimeFrame, candlestickSeries);  
            } else {
                setChartData(chartTimeFrame, candlestickSeries);
            }
        }    
    });
})
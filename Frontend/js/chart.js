import { createChart } from '/node_modules/lightweight-charts/dist/lightweight-charts.standalone.development.mjs';

/*
const button = document.getElementById('new-candle');


button.addEventListener('click', function () {
    fetch("http://127.0.0.1:5000/api/new-candle?tf=15m", {
        method: "POST"})

    .then(response => response.json())
    .then(newCandleData => {
        candlestickSeries.update(newCandleData);
    
    })
});


fetch("http://127.0.0.1:5000/api/get-chart-data?tf=15m", {
        method: "POST"})
    .then(response => response.json())  
    .then(chartData => {
        candlestickSeries.setData(chartData);
        chart.timeScale().fitContent(); 
})

*/



function createCandle(timeFrame) {
    const chartContainer = document.getElementById(timeFrame)
    const chart = createChart(chartContainer, { width: 500, height: 500 });
    const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
        wickUpColor: '#26a69a', wickDownColor: '#ef5350',
    });

    chart.priceScale('right').applyOptions({
        ticksVisible: true
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


function updateChart(timeFrame){
    return 1
}


const timeFrames = ["1m", "15m"]; // , "4h", "1h"
var charts = {};

var chartUpdates = [];

timeFrames.forEach(timeFrame => {
    charts[timeFrame] = createCandle(timeFrame);
    chartUpdates.push({
        "tf": timeFrame, 
        "button": document.getElementById(`${timeFrame}-new-candle`)
    });
})

chartUpdates.forEach(updateData => {

    let timeFrame = updateData["tf"]
    let button = updateData["button"]

    button.addEventListener('click', function () {
        fetch(`http://127.0.0.1:5000/api/new-candle?tf=${timeFrame}`, {
            method: "POST"})
    
        .then(response => response.json())
        .then(newCandleData => {
            charts[timeFrame]["candle"].update(newCandleData);
        
        })
    });
})


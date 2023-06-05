import { createChart } from '/node_modules/lightweight-charts/dist/lightweight-charts.standalone.development.mjs';


const button = document.getElementById('new-candle');

const chartContainer = document.getElementById("chart-container")
const chart = createChart(chartContainer, { width: 1000, height: 500 });
const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
    wickUpColor: '#26a69a', wickDownColor: '#ef5350',
});

chart.priceScale('right').applyOptions({
    ticksVisible: true
})

button.addEventListener('click', function () {
    fetch("http://127.0.0.1:5000/api/new-candle", {
        method: "POST"})

    .then(response => response.json())
    .then(newCandleData => {
        candlestickSeries.update(newCandleData);
    
    })
});


fetch("http://127.0.0.1:5000/api/get-chart-data", {
        method: "POST"})
    .then(response => response.json())  
    .then(chartData => {
        candlestickSeries.setData(chartData);
        chart.timeScale().fitContent(); 
})




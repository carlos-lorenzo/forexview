import { createChart } from '/node_modules/lightweight-charts/dist/lightweight-charts.standalone.development.mjs';

import { updateBroker } from "/Frontend/js/broker.js"



function createCandleChart(timeFrame) {
    let chartContainer = document.createElement("div");
    chartContainer.className = "chart";
    chartContainer.id = timeFrame;
    console.log();
    let chartWidth = (window.innerWidth * 0.4)
    let chartHeight = (window.innerHeight * 0.6)

    const chart = createChart(chartContainer, {
        height: chartHeight, 
        width: chartWidth,
        layout: {
            background: {
                color: '#131722',  
            },
            textColor: "white",
            fontFamily: "'Orbitron', sans-serif"
        }
        
    
    });

    

    const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a', 
        downColor: '#ef5350', 
        borderVisible: true,
        wickUpColor: '#26a69a', 
        wickDownColor: '#ef5350', 
        priceFormat: { type: 'price', precision: 5, minMove: 0.00001 },
        
    });


    chart.priceScale('right').applyOptions({
        ticksVisible: true,
    })

    chart.applyOptions({
        background: {type: "solid", "color": "red"}
    })

    candlestickSeries.applyOptions({
        title: timeFrame,
       
    })

    fetch(`http://127.0.0.1:5000/api/get-chart-data?tf=${timeFrame}&pair=EURUSD`, {
        method: "POST"})
    .then(response => response.json())  
    .then(chartData => {
        candlestickSeries.setData(chartData);
        chart.timeScale().fitContent();

    })

    let chartsContainer = document.getElementById("charts");

    chartsContainer.appendChild(chartContainer);


    return {
        "chart": chart,
        "candle": candlestickSeries
    }
}


function setChartData(timeFrame, candlestickSeries){
    fetch(`http://127.0.0.1:5000/api/get-chart-data?tf=${timeFrame}&pair=EURUSD`, {
        method: "POST"})
    .then(response => response.json())  
    .then(chartData => {
        candlestickSeries.setData(chartData);
    })
}

function updateChart(timeFrame,  candlestickSeries){
    fetch(`http://127.0.0.1:5000/api/new-candle?tf=${timeFrame}&pair=EURUSD`, {
            method: "POST"})  
        .then(response => response.json())
        .then(newCandleData => {
            candlestickSeries.update(newCandleData);
    })
}

function createCharts(timeFrames) {
    charts = {};
    timeFrames.forEach(timeFrame => {
        charts[timeFrame] = createCandleChart(timeFrame);
    })

    return charts;
}


function setTimeDials(timeFrames, charts) {
    let timeDials = document.getElementById("time-dials");
    timeDials.innerHTML = "";
    
    timeFrames.forEach(timeFrame => {
        let newCandleButton = document.createElement("button");
        newCandleButton.innerHTML = `Add ${timeFrame}`
        newCandleButton.addEventListener("click", function () {

            fetch(`http://127.0.0.1:5000/api/update-time?tf=${timeFrame}&pair=EURUSD`, {method: "GET"})

            for (let chartTimeFrame in charts) {
                let candlestickSeries = charts[chartTimeFrame]["candle"];

                if (chartTimeFrame == timeFrame) {
                    updateChart(chartTimeFrame, candlestickSeries);  
                } else {
                    setChartData(chartTimeFrame, candlestickSeries);
                }
            }
        })

        timeDials.appendChild(newCandleButton);

    })
}

function drawTimeFrameSelectors(validTimeFrames) {
    const timeFrameSelectors = document.getElementById("timeframe-selectors");
    timeFrameSelectors.innerHTML = "";
    validTimeFrames.forEach(timeFrame => {
        let timeFrameSelector = document.createElement("div");
        timeFrameSelector.className = "timeframe-selector";
        timeFrameSelector.id = `${timeFrame}-selector`
        timeFrameSelector.onclick = openTimeFrame;
        
        timeFrameSelector.innerHTML = timeFrame;

        let currentTimeFrame = fetchTimeFrameToDraw(validTimeFrames)[0];
        if (timeFrame == currentTimeFrame) {
            timeFrameSelector.style.color = "#1E53E5";
        } else {
            timeFrameSelector.style.color = "white";
        }
        timeFrameSelector.style.cursor = "pointer";
        

        timeFrameSelectors.appendChild(timeFrameSelector);
    })
}

function openTimeFrame(pointerEvent) {
    
    window.open(`http://127.0.0.1:5500/Frontend/html/?tf=${pointerEvent.target.innerHTML}`, "_self");
    
}

function fetchTimeFrameToDraw(validTimeFrames) {
    const urlParams = new URLSearchParams(window.location.search);
    const timeFrame = urlParams.get("tf")

    if (validTimeFrames.includes(timeFrame)){
        
        return [timeFrame];
    } else {
        return ["15m"]
    }
    
}



const validTimeFrames = ["1m", "15m", "4h", "1D"]
const timeFrames = fetchTimeFrameToDraw(validTimeFrames);


var charts = createCharts(timeFrames);
drawTimeFrameSelectors(validTimeFrames);
setTimeDials(validTimeFrames, charts);

document.getElementById("reset").addEventListener("click", function(){
    fetch("http://127.0.0.1:5000/api/reset?pair=EURUSD", {
        method: "POST"})
    .then(function() {
        document.getElementById("charts").innerHTML = "";
        document.getElementById("time-dials").innerHTML = "";
        updateBroker();
        
        charts = createCharts(timeFrames);
        drawTimeFrameSelectors(validTimeFrames);
        setTimeDials(validTimeFrames, charts);
    })
})

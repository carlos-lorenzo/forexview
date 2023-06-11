import { createChart } from '/node_modules/lightweight-charts/dist/lightweight-charts.standalone.development.mjs';

const chart = createChart(document.getElementById('chart'), { width: 500, height: 500 });


const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
    wickUpColor: '#26a69a', wickDownColor: '#ef5350',
});

candlestickSeries.setData([
    { time: 1, open: 75.16, high: 82.84, low: 36.16, close: 45.72 },
    { time: 2, open: 45.12, high: 53.90, low: 45.12, close: 48.09 },
    { time: 3, open: 60.71, high: 60.71, low: 53.39, close: 59.29 },
    { time: 4, open: 68.26, high: 68.26, low: 59.04, close: 60.50 },
    { time: 5, open: 67.71, high: 105.85, low: 66.67, close: 91.04 },
]);

chart.timeScale().fitContent();
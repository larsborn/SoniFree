import colorLib from '@kurkle/color';
import Chart from 'chart.js/auto'


(async function () {
    function transparentize(value, opacity) {
        const alpha = opacity === undefined ? 0.5 : 1 - opacity;
        return colorLib(value).alpha(alpha).rgbString();
    }

    const followerCountJson = require('./data/follower_count.json');
    followerCountJson.data.datasets = followerCountJson.data.datasets.map((dataset) => ({
        ...dataset,
        "backgroundColor": transparentize(dataset.borderColor, 0.5),
    }))
    new Chart(document.getElementById('follower_count'), followerCountJson);

    const listenerCountJson = require('./data/listener_count.json');
    listenerCountJson.data.datasets = listenerCountJson.data.datasets.map((dataset) => ({
        ...dataset,
        "backgroundColor": transparentize(dataset.borderColor, 0.5),
    }))
    new Chart(document.getElementById('listener_count'), listenerCountJson);

    const consumptionSecondsCountJson = require('./data/consumption_seconds.json');
    consumptionSecondsCountJson.data.datasets = consumptionSecondsCountJson.data.datasets.map((dataset) => ({
        ...dataset,
        "backgroundColor": transparentize(dataset.borderColor, 0.5),
    }))
    new Chart(document.getElementById('consumption_seconds'), consumptionSecondsCountJson);

    const streamCountJson = require('./data/stream_count.json');
    streamCountJson.data.datasets = streamCountJson.data.datasets.map((dataset) => ({
        ...dataset,
        "backgroundColor": transparentize(dataset.borderColor, 0.5),
    }))
    new Chart(document.getElementById('stream_count'), streamCountJson);

    const streamStartCountJson = require('./data/stream_start_count.json');
    streamStartCountJson.data.datasets = streamStartCountJson.data.datasets.map((dataset) => ({
        ...dataset,
        "backgroundColor": transparentize(dataset.borderColor, 0.5),
    }))
    new Chart(document.getElementById('stream_start_count'), streamStartCountJson);
})();

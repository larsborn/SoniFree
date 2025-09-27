import colorLib from '@kurkle/color';
import Chart from 'chart.js/auto'

function humandReadbleSeconds(seconds) {
    const units = {
        "year": 24 * 60 * 60 * 365,
        "month": 24 * 60 * 60 * 30,
        "week": 24 * 60 * 60 * 7,
        "day": 24 * 60 * 60,
        "hour": 60 * 60,
        "minute": 60,
        "second": 1,
    }

    var result = []

    for (let name in units) {
        const p = Math.floor(seconds / units[name]);
        if (p === 1) result.push(p + " " + name);
        if (p >= 2) result.push(p + " " + name + "s");
        seconds %= units[name]
    }
    let prefix = "";
    if (result.length > 2) {
        result = result.slice(0, 2);
        prefix = "~"
    }

    return prefix + result.join(", ");
}

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

    const sums = require('./data/sums.json');
    document.getElementById("followers").textContent = sums.followers;
    document.getElementById("listeners").textContent = sums.listeners;
    document.getElementById("consumed").textContent = humandReadbleSeconds(sums.consumed);
    document.getElementById("streams").textContent = sums.streams;
})();

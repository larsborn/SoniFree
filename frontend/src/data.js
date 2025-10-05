import colorLib from '@kurkle/color';
import Chart from 'chart.js/auto'

const verticalLinePlugin = {
    getLinePosition: function (chart, pointIndex) {
        const meta = chart.getDatasetMeta(0); // first dataset is used to discover X coordinate of a point
        const data = meta.data;
        return data[pointIndex].x;
    },

    renderVerticalLine: function (chartInstance, pointIndex, caption) {
        const lineLeftOffset = this.getLinePosition(chartInstance, pointIndex);
        const scale = chartInstance.scales.y;

        chartInstance.ctx.beginPath();
        chartInstance.ctx.strokeStyle = '#5a0d0d';
        chartInstance.ctx.moveTo(lineLeftOffset, scale.top);
        chartInstance.ctx.lineTo(lineLeftOffset, scale.bottom);
        chartInstance.ctx.stroke();
    },

    beforeDatasetsDraw: function (chart, easing) {
        if (chart.config._config.lineAtIndex) {
            chart.config._config.lineAtIndex.forEach(
                ({index, caption}) => this.renderVerticalLine(chart, index, caption)
            );
        }
    }
};

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

    function dumpDiagram(id, data) {
        data.data.datasets = data.data.datasets.map((dataset) => ({
            ...dataset,
            "backgroundColor": transparentize(dataset.borderColor, 0.5),
        }))
        new Chart(document.getElementById(id), {...data, plugins: [verticalLinePlugin]});
    }

    dumpDiagram("follower_count", require(`./data/follower_count.json`));
    dumpDiagram("listener_count", require(`./data/listener_count.json`));
    dumpDiagram("engaged_listener_count", require(`./data/engaged_listener_count.json`));
    dumpDiagram("consumption_seconds", require(`./data/consumption_seconds.json`));
    dumpDiagram("stream_count", require(`./data/stream_count.json`));
    dumpDiagram("stream_start_count", require(`./data/stream_start_count.json`));

    const aggregates = require('./data/aggregates.json');
    document.getElementById("followers").textContent = aggregates.sum.followers;
    document.getElementById("listeners").textContent = aggregates.sum.listeners;
    document.getElementById("consumed").textContent = humandReadbleSeconds(aggregates.sum.consumed);
    document.getElementById("streams").textContent = aggregates.sum.streams;

    let lastDates = []

    let providerList = Object.keys(aggregates.by_provider);
    providerList.sort()
    providerList.map((provider) => {
        lastDates.push(`${provider} (${aggregates.by_provider[provider].last_date})`);
    });

    document.getElementById("last-dates").textContent = lastDates.join(", ");
})();

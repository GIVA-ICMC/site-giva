(function () {
  var el = document.getElementById("citations-year-chart");
  var dataEl = document.getElementById("citations-year-data");
  if (!el || !dataEl || typeof Plotly === "undefined") return;

  var payload;
  try {
    payload = JSON.parse(dataEl.textContent || "{}");
    if (typeof payload === "string") payload = JSON.parse(payload);
  } catch (err) {
    return;
  }

  var years = payload.years || [];
  var series = payload.series || [];
  if (!years.length || !series.length) return;

  var totals = years.map(function (_, i) {
    return series.reduce(function (sum, item) {
      var value = item.values[i];
      return sum + (typeof value === "number" ? value : 0);
    }, 0);
  });

  var traces = [
    {
      type: "scatter",
      mode: "lines+markers",
      name: "All faculty",
      x: years,
      y: totals,
      hovertemplate: "%{x}: %{y:,} citations<extra></extra>",
      line: {
        color: "#1a73e8",
        width: 3.2,
        shape: "spline",
        smoothing: 0.6,
      },
      marker: {
        color: "#1a73e8",
        size: 8,
        line: { color: "#ffffff", width: 1.6 },
      },
      fill: "tozeroy",
      fillcolor: "rgba(26, 115, 232, 0.16)",
    },
  ];

  var layout = {
    margin: { t: 6, r: 8, b: 32, l: 46 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    showlegend: false,
    hovermode: "x unified",
    hoverlabel: {
      bgcolor: "#0a2c57",
      bordercolor: "#0a2c57",
      font: { color: "#ffffff", size: 12, family: "system-ui, sans-serif" },
    },
    font: {
      family: "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
      color: "#1f2937",
      size: 13,
    },
    xaxis: {
      title: "",
      dtick: 2,
      tickfont: { size: 12, color: "#6b7280" },
      gridcolor: "rgba(10, 44, 87, 0.06)",
      zeroline: false,
      showline: false,
      fixedrange: true,
    },
    yaxis: {
      title: { text: "Citations", font: { size: 12, color: "#6b7280" } },
      tickfont: { size: 12, color: "#6b7280" },
      gridcolor: "rgba(10, 44, 87, 0.08)",
      zeroline: false,
      separatethousands: true,
      fixedrange: true,
    },
  };

  var config = {
    displayModeBar: false,
    responsive: true,
  };

  Plotly.newPlot(el, traces, layout, config);

  window.addEventListener("resize", function () {
    Plotly.Plots.resize(el);
  });
})();

import "./App.css";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {

  const riskData = {
    labels: [
      "01 Aug",
      "15 Aug",
      "30 Aug",
      "10 Sep",
      "20 Sep",
      "30 Sep"
    ],

    datasets: [
  {
    label: "AI Risk %",
    data: [48, 44, 41, 39, 35, 32],
    tension: 0.3,
    borderColor: "#2563eb",
    backgroundColor: "rgba(37, 99, 235, 0.1)",
    pointRadius: 5,
    pointHoverRadius: 7,
    borderWidth: 3,
  },
],
  };

  const riskOptions = {
    responsive: true,

    plugins: {
      legend: {
        display: true,
      },

      title: {
        display: true,
        text: "AI Health Risk Trend",
      },
    },

    scales: {
      y: {
        beginAtZero: true,
        max: 100,

        title: {
          display: true,
          text: "Risk Percentage",
        },
      },

      x: {
        title: {
          display: true,
          text: "Assessment Date",
        },
      },
    },
  };

  return (
    <div className="app">

      <header className="dashboard-header">
        <div>
          <h1>MedIntel</h1>
          <p>Health Tracking & Analytics</p>
        </div>

        <div className="patient-info">
          <span>Patient Dashboard</span>
        </div>
      </header>

      <section className="welcome-section">
        <h2>Health Overview</h2>

        <p>
          Track your health parameters and AI risk predictions over time.
        </p>
      </section>

      <section className="summary-cards">

        <div className="card">
          <h3>Latest AI Risk</h3>
          <div className="card-value">32%</div>
          <p>Lower Risk</p>
        </div>

        <div className="card">
          <h3>Previous Risk</h3>
          <div className="card-value">38%</div>
          <p>Previous Assessment</p>
        </div>

        <div className="card">
          <h3>Total Assessments</h3>
          <div className="card-value">5</div>
          <p>Health assessments</p>
        </div>

        <div className="card">
          <h3>Last Assessment</h3>
          <div className="card-value">30 Sep</div>
          <p>2026</p>
        </div>

      </section>

      <section className="health-section">

        <h2>Current Health Parameters</h2>

        <div className="parameter-cards">

          <div className="parameter-card">
            <h3>BMI</h3>
            <strong>23.4</strong>
            <p>kg/m²</p>
          </div>

          <div className="parameter-card">
            <h3>Blood Glucose</h3>
            <strong>108</strong>
            <p>mg/dL</p>
          </div>

          <div className="parameter-card">
            <h3>HbA1c</h3>
            <strong>5.6</strong>
            <p>%</p>
          </div>

        </div>

      </section>

      <section className="chart-section">

        <h2>AI Risk Trend</h2>

        <Line data={riskData} options={riskOptions} />

      </section>
      {/* Assessment History */}

<section className="history-section">

  <h2>Health Assessment History</h2>

  <p>
    Previous health assessments and AI risk predictions.
  </p>

  <div className="table-container">

    <table>

      <thead>
        <tr>
          <th>Date</th>
          <th>BMI</th>
          <th>Blood Glucose</th>
          <th>HbA1c</th>
          <th>AI Risk</th>
          <th>Risk Level</th>
        </tr>
      </thead>

      <tbody>

        <tr>
          <td>30 Sep 2026</td>
          <td>23.4</td>
          <td>108 mg/dL</td>
          <td>5.6%</td>
          <td>32%</td>
          <td>Lower Risk</td>
        </tr>

        <tr>
          <td>20 Sep 2026</td>
          <td>23.7</td>
          <td>112 mg/dL</td>
          <td>5.8%</td>
          <td>35%</td>
          <td>Lower Risk</td>
        </tr>

        <tr>
          <td>10 Sep 2026</td>
          <td>24.1</td>
          <td>118 mg/dL</td>
          <td>6.0%</td>
          <td>39%</td>
          <td>Higher Risk</td>
        </tr>

        <tr>
          <td>30 Aug 2026</td>
          <td>24.5</td>
          <td>124 mg/dL</td>
          <td>6.2%</td>
          <td>41%</td>
          <td>Higher Risk</td>
        </tr>

        <tr>
          <td>15 Aug 2026</td>
          <td>24.8</td>
          <td>130 mg/dL</td>
          <td>6.4%</td>
          <td>44%</td>
          <td>Higher Risk</td>
        </tr>

      </tbody>

    </table>

  </div>

</section>
{/* Previous vs Current Assessment */}

<section className="comparison-section">

  <h2>Previous vs Current Assessment</h2>

  <p>
    Compare your latest health assessment with the previous assessment.
  </p>

  <div className="comparison-table-container">

    <table>

      <thead>
        <tr>
          <th>Health Parameter</th>
          <th>Previous</th>
          <th>Current</th>
          <th>Change</th>
        </tr>
      </thead>

      <tbody>

        <tr>
          <td>BMI</td>
          <td>23.7</td>
          <td>23.4</td>
          <td>↓ 0.3</td>
        </tr>

        <tr>
          <td>Blood Glucose</td>
          <td>112 mg/dL</td>
          <td>108 mg/dL</td>
          <td>↓ 4 mg/dL</td>
        </tr>

        <tr>
          <td>HbA1c</td>
          <td>5.8%</td>
          <td>5.6%</td>
          <td>↓ 0.2%</td>
        </tr>

        <tr>
          <td>AI Risk</td>
          <td>35%</td>
          <td>32%</td>
          <td>↓ 3%</td>
        </tr>

      </tbody>

    </table>

  </div>

</section>

    </div>
  );
} 

export default App;
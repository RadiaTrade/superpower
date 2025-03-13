import React from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const sampleData = {
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  datasets: [
    {
      label: "Price Trend",
      data: [100, 120, 140, 130, 160, 180],
      borderColor: "rgba(0, 255, 255, 1)",
      backgroundColor: "rgba(0, 255, 255, 0.2)",
      borderWidth: 2,
      fill: true,
    },
  ],
};

export default function Chart() {
  return (
    <div className="bg-black border border-white p-4 rounded-xl shadow-lg max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold font-orbitron text-center">Live Market Chart</h2>
      <Line data={sampleData} />
    </div>
  );
}

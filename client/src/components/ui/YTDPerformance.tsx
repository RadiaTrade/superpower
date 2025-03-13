import React from "react";

interface YTDPerformanceProps {
  startingBalance: number;
  ytdPerformance: number;
}

const YTDPerformance: React.FC<YTDPerformanceProps> = ({ startingBalance, ytdPerformance }) => {
  // Calculate YTD Profit
  const ytdProfit = ytdPerformance - startingBalance;

  // Calculate YTD ROI%
  const ytdROI = ((ytdProfit / startingBalance) * 100).toFixed(2);

  return (
    <div className="bg-black border border-white p-6 rounded-2xl shadow-xl max-w-lg text-center">
      <h2 className="text-2xl font-semibold font-orbitron text-white">YTD Performance</h2>
      <p className="mt-2 text-gray-400">Current: ${ytdPerformance.toFixed(2)}</p>
      <p className="mt-2 text-green-400">YTD Profit: ${ytdProfit.toFixed(2)}</p>
      <p className="mt-2 text-blue-400">YTD ROI: {ytdROI}%</p>
    </div>
  );
};

export default YTDPerformance;

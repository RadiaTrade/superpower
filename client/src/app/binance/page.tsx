"use client"; // ✅ Ensures this is a Client Component

import React from 'react';
import Link from 'next/link';

export default function BinancePage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center px-6 py-12">

      {/* Binance Paper Trading Dashboard */}
      <div className="text-center bg-black border border-white p-10 rounded-2xl shadow-2xl max-w-[800px]">
        <h1 className="text-4xl font-orbitron font-extrabold">Binance Paper Trading Dashboard</h1>
        <p className="mt-4 text-lg text-gray-300">
          Simulated AI trading with real-time Binance market data.
        </p>
        <div className="mt-6">
          <Link href="/">
            <button className="w-full border-2 border-black bg-white text-black text-lg font-bold uppercase tracking-wide px-6 py-3 rounded-lg transition-all hover:bg-black hover:text-white hover:border-white">
              HOME
            </button>
          </Link>
        </div>
      </div>

      {/* Stats Row - Daily ROI%, Unrealized P&L, Total Value */}
      <div className="mt-12 flex flex-wrap justify-center gap-8 max-w-7xl text-center">

        {/* Daily ROI% */}
        <div className="bg-black border border-white p-6 rounded-2xl shadow-2xl w-[280px] h-[150px] flex flex-col items-center justify-center">
          <h2 className="text-lg font-orbitron text-white">Daily ROI%</h2>
          <p className="text-xl text-green-400">+3.25%</p>
        </div>

        {/* Unrealized P&L */}
        <div className="bg-black border border-white p-6 rounded-2xl shadow-2xl w-[280px] h-[150px] flex flex-col items-center justify-center">
          <h2 className="text-lg font-orbitron text-white">Unrealized P&L</h2>
          <p className="text-xl text-yellow-400">+0.89%</p>
        </div>

        {/* Total Portfolio Value */}
        <div className="bg-black border border-white p-6 rounded-2xl shadow-2xl w-[280px] h-[150px] flex flex-col items-center justify-center">
          <h2 className="text-lg font-orbitron text-white">Total Portfolio Value</h2>
          <p className="text-xl text-blue-400">$25,647.32</p>
        </div>
      </div>

      {/* Trading Controls */}
      <div className="mt-12 bg-black border border-white p-6 rounded-2xl shadow-2xl max-w-[600px] w-full text-center">
        <h2 className="text-2xl font-semibold font-orbitron mb-4">Trading Controls</h2>
        <div className="flex justify-center gap-6">
          <button className="w-44 border-2 border-black bg-white text-black text-lg font-bold uppercase tracking-wide px-6 py-3 rounded-lg transition-all hover:bg-black hover:text-white hover:border-white">
            START TRADING
          </button>
          <button className="w-44 border-2 border-black bg-white text-black text-lg font-bold uppercase tracking-wide px-6 py-3 rounded-lg transition-all hover:bg-black hover:text-white hover:border-white">
            STOP TRADING
          </button>
        </div>
      </div>

      {/* Live Market Chart */}
      <div className="mt-12 bg-black border border-white p-6 rounded-2xl shadow-2xl max-w-[700px] w-full text-center">
        <h2 className="text-2xl font-orbitron font-semibold">Live Market Chart</h2>
        <div className="mt-4 bg-gray-800 rounded-lg h-[200px] flex items-center justify-center w-full">
          {/* Placeholder for Chart - To be integrated */}
          <p className="text-gray-500">[ Chart Placeholder ]</p>
        </div>
      </div>

      {/* YTD Performance */}
      <div className="mt-12 bg-black border border-white p-6 rounded-2xl shadow-2xl max-w-[400px] text-center">
        <h2 className="text-2xl font-orbitron font-semibold">📅 YTD Performance</h2>
        <div className="mt-4 flex flex-col justify-center items-center text-white text-lg">
          <div className="flex items-center gap-2">
            <p>📊 YTD ROI%</p>
            <span className="text-green-400 text-xl">+15.42%</span>
          </div>
          <div className="flex items-center gap-2">
            <p>💰 YTD Profit</p>
            <span className="text-green-400 text-xl">$8,930.78</span>
          </div>
        </div>
      </div>

      {/* Trade Execution Logs */}
      <div className="mt-12 bg-black border border-white p-6 rounded-2xl shadow-2xl max-w-[500px] text-center">
        <h2 className="text-2xl font-orbitron font-semibold">📜 Trade Execution Logs</h2>
        <p className="text-gray-300 mt-2">Last Trade: Bought 0.05 BTC at $62,450</p>
      </div>

    </div>
  );
}

"use client"; // ✅ Ensures this is a Client Component

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

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
            <button className="w-full">HOME</button>
          </Link>
        </div>
      </div>

      {/* Trading Controls */}
      <div className="mt-12 bg-black border border-white p-6 rounded-2xl shadow-2xl max-w-[600px] w-full text-center">
        <h2 className="text-2xl font-semibold font-orbitron mb-4">Trading Controls</h2>
        <div className="flex justify-center gap-6">
          <button className="w-44">START TRADING</button>
          <button className="w-44">STOP TRADING</button>
        </div>
      </div>

    </div>
  );
}

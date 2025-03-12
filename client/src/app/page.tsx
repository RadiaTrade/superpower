import React from "react";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-6 py-12">
      
      {/* Hero Section */}
      <div className="text-center bg-black border border-white p-10 rounded-2xl shadow-2xl max-w-4xl">
        <h1 className="text-5xl font-extrabold font-orbitron">RadiaTrade AI</h1>
        <p className="text-xl mt-4 text-gray-300">Next-Generation AI-Powered Trading</p>
        <div className="mt-6">
          <Button className="w-full bg-gradient-to-b from-gray-900 to-black shadow-lg">GET STARTED</Button>
        </div>
      </div>

      {/* Trading Sections (Fixed Transparency & Alignment) */}
      <div className="mt-16 flex flex-wrap justify-center gap-8 max-w-7xl text-center">
        
        {/* Binance Trading */}
        <div className="bg-black border border-white p-8 rounded-2xl shadow-2xl w-[320px]">
          <h2 className="text-2xl font-semibold font-orbitron text-white">Binance Trading</h2>
          <p className="mt-2 text-gray-400">Trade Crypto with AI-powered strategies.</p>
          <div className="mt-6 w-full">
            <Button className="w-full bg-gradient-to-b from-gray-900 to-black shadow-lg text-white">TRADE ON BINANCE</Button>
          </div>
        </div>

        {/* AI Trading */}
        <div className="bg-black border border-white p-8 rounded-2xl shadow-2xl w-[320px]">
          <h2 className="text-2xl font-semibold font-orbitron text-white">Binance & IBKR</h2>
          <p className="mt-2 text-gray-400">Trade all assets with AI, optimized for maximum efficiency.</p>
          <div className="mt-6 w-full">
            <Button className="w-full bg-gradient-to-b from-gray-900 to-black shadow-lg text-white">EXPLORE AI TRADING</Button>
          </div>
        </div>

        {/* Interactive Brokers */}
        <div className="bg-black border border-white p-8 rounded-2xl shadow-2xl w-[320px]">
          <h2 className="text-2xl font-semibold font-orbitron text-white">Interactive Brokers</h2>
          <p className="mt-2 text-gray-400">Trade Stocks, Options, and Forex with AI.</p>
          <div className="mt-6 w-full">
            <Button className="w-full bg-gradient-to-b from-gray-900 to-black shadow-lg text-white">TRADE ON IBKR</Button>
          </div>
        </div>

      </div>

      {/* Need Help Section (Fixed Spacing Below Trading Sections) */}
      <div className="mt-20 text-center bg-black border border-white p-8 rounded-2xl shadow-2xl max-w-4xl">
        <h2 className="text-2xl font-semibold font-orbitron text-white">Need Help?</h2>
        <p className="mt-2 text-gray-400">Chat with the world’s most powerful trading AI.</p>
        <div className="mt-6">
          <Button className="w-full bg-gradient-to-b from-gray-900 to-black shadow-lg text-white">OPEN CHAT</Button>
        </div>
      </div>

    </div>
  );
}

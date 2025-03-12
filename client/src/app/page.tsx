import React from "react";
import { Button } from "../../components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-6 py-12">
      
      {/* Hero Section */}
      <div className="w-full max-w-3xl bg-black border border-white p-10 rounded-xl shadow-xl text-center mb-12">
        <h1 className="text-5xl font-extrabold text-white tracking-wide">
          RadiaTrade AI
        </h1>
        <p className="text-xl mt-4 text-gray-300">Next-Generation AI-Powered Trading</p>
        <div className="mt-6">
          <Button>Get Started</Button>
        </div>
      </div>

      {/* Trading Sections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
        
        {/* Binance Trading */}
        <div className="bg-black border border-white p-8 rounded-xl shadow-lg text-center">
          <h2 className="text-2xl font-bold text-white">Binance Trading</h2>
          <p className="mt-2 text-gray-300">Trade Crypto with AI-powered strategies.</p>
          <div className="mt-6">
            <Button>Trade on Binance</Button>
          </div>
        </div>

        {/* AI Trading Section */}
        <div className="bg-black border border-white p-8 rounded-xl shadow-lg text-center">
          <h2 className="text-2xl font-bold text-white">Binance & IBKR</h2>
          <p className="mt-2 text-gray-300">Trade all assets with AI, optimized for maximum efficiency.</p>
          <div className="mt-6">
            <Button>Explore AI Trading</Button>
          </div>
        </div>

        {/* Interactive Brokers */}
        <div className="bg-black border border-white p-8 rounded-xl shadow-lg text-center">
          <h2 className="text-2xl font-bold text-white">Interactive Brokers</h2>
          <p className="mt-2 text-gray-300">Trade Stocks, Options, and Forex with AI.</p>
          <div className="mt-6">
            <Button>Trade on IBKR</Button>
          </div>
        </div>

      </div>

      {/* Chat Support Section */}
      <div className="mt-12 w-full max-w-3xl bg-black border border-white p-8 rounded-xl shadow-lg text-center">
        <h2 className="text-2xl font-bold text-white">Need Help?</h2>
        <p className="mt-2 text-gray-300">Chat with the world’s most powerful trading AI.</p>
        <div className="mt-6">
          <Button>Open Chat</Button>
        </div>
      </div>

    </div>
  );
}

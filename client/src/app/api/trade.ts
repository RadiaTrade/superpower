import { NextRequest, NextResponse } from "next/server";
import axios from "axios";
import crypto from "crypto";

// ✅ Your Binance Testnet API Keys
const API_KEY = process.env.BINANCE_API_KEY!;
const SECRET_KEY = process.env.BINANCE_SECRET_KEY!;
const BASE_URL = "https://testnet.binance.vision";

// ✅ Generate a valid timestamp
function getTimestamp(): number {
  return Date.now();
}

// ✅ Create HMAC SHA256 Signature
function createSignature(params: Record<string, string | number>): string {
  const queryString = Object.entries(params)
    .map(([key, val]) => `${key}=${val}`)
    .join("&");

  return crypto.createHmac("sha256", SECRET_KEY).update(queryString).digest("hex");
}

// ✅ Handle API Requests
export async function POST(req: NextRequest) {
  try {
    const { symbol, quantity } = await req.json();

    if (!symbol || !quantity) {
      return NextResponse.json({ error: "Missing trade parameters." }, { status: 400 });
    }

    const timestamp = getTimestamp();
    const params: Record<string, string | number> = {
      symbol: symbol.toUpperCase(),
      side: "BUY",
      type: "MARKET",
      quantity: quantity.toFixed(6), // Ensure correct decimal places
      timestamp,
    };

    params["signature"] = createSignature(params);

    const headers = {
      "X-MBX-APIKEY": API_KEY,
    };

    const response = await axios.post(`${BASE_URL}/api/v3/order`, null, { params, headers });

    return NextResponse.json({ orderId: response.data.orderId });
  } catch (error: any) {
    return NextResponse.json({ error: error.response?.data || "Trade execution failed." }, { status: 500 });
  }
}

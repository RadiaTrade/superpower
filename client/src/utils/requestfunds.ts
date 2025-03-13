import axios from "axios";
import crypto from "crypto";

// ✅ Your Binance Testnet API Keys
const API_KEY = "FEf8x3XU32Hd3a923iT3erconZrmhW77dfXKdpfjMAjpBmW8Ckmv6Fz3RSnVe2Yr";
const SECRET_KEY = "LJyOthF5Ohvq24QcVpujHGymjjpRttyn4b6C65qiDOSVNBJNsawAAfdqClQ3un1N";

// ✅ Binance Testnet API Base URL
const BASE_URL = "https://testnet.binance.vision";

// ✅ Assets to request funds for
const assets = ["BTC", "USDT", "ETH"];

// ✅ Generate a valid timestamp
function getTimestamp(): number {
  return Date.now();
}

// ✅ Create HMAC SHA256 Signature
function createSignature(queryString: string): string {
  return crypto.createHmac("sha256", SECRET_KEY).update(queryString).digest("hex");
}

// ✅ Request account balance (for debugging)
async function getAccountBalance() {
  const timestamp = getTimestamp();
  const queryString = `timestamp=${timestamp}`;
  const signature = createSignature(queryString);

  const headers = {
    "X-MBX-APIKEY": API_KEY,
  };

  const url = `${BASE_URL}/api/v3/account?${queryString}&signature=${signature}`;

  try {
    const response = await axios.get(url, { headers });
    console.log("✅ Binance Testnet Balance:", response.data.balances);
  } catch (error: any) {
    console.error("❌ Failed to get account balance:", error.response?.data || error.message);
  }
}

// ✅ Run the balance check first
getAccountBalance();

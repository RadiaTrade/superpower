import { Inter, Orbitron } from "next/font/google"; // FIXED IMPORT
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const orbitron = Orbitron({
  subsets: ["latin"],
  weight: ["400", "700"], // Normal & Bold weights
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>RadiaTrade AI</title>
        <meta name="description" content="AI-powered trading with Binance & Interactive Brokers" />
      </head>
      <body className={inter.className}>
        <div className="navbar">
          <button className="nav-button">Sign Up</button>
          <button className="nav-button">Login</button>
        </div>
        <div className="container">{children}</div>
      </body>
    </html>
  );
}
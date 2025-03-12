import "./globals.css";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white">
        {/* Navigation Bar */}
        <div className="navbar">
          <img src="/home-icon.png" alt="Home" className="home-icon" />
          <button className="nav-button">SIGN UP</button>
          <button className="nav-button">LOGIN</button>
        </div>

        {/* Page Content */}
        {children}
      </body>
    </html>
  );
}

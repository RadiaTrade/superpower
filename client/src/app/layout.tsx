"use client";

import "./globals.css";
import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white">
        
        {/* Navigation Bar */}
        <div className="navbar flex justify-between items-center p-4">
          
          {/* Home Button - NO ICON, JUST TEXT */}
          <Link href="/">
            <Button className="px-4 py-2 text-sm bg-gray-800 text-white font-bold rounded-md shadow-md hover:bg-gray-700 border border-black tracking-wide [text-shadow:_1px_1px_2px_black]">
              HOME
            </Button>
          </Link>

          {/* Sign Up & Login Buttons */}
          <div className="flex gap-4">
            <Link href="/signup">
              <Button className="px-4 py-2 text-sm bg-blue-600 text-white font-bold rounded-md shadow-md hover:bg-blue-500 border border-black tracking-wide [text-shadow:_1px_1px_2px_black]">
                SIGN UP
              </Button>
            </Link>
            <Link href="/login">
              <Button className="px-4 py-2 text-sm bg-green-600 text-white font-bold rounded-md shadow-md hover:bg-green-500 border border-black tracking-wide [text-shadow:_1px_1px_2px_black]">
                LOGIN
              </Button>
            </Link>
          </div>
        </div>

        {/* Page Content */}
        {children}

      </body>
    </html>
  );
}

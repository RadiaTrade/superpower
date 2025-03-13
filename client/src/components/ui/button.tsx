"use client"; // ✅ Ensures this is a Client Component

import React from "react";
import Link from "next/link";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({ children, onClick, href, className }) => {
  const buttonStyle =
    "w-full px-6 py-3 bg-gradient-to-b from-black to-gray-800 text-white font-bold border border-white rounded-2xl shadow-md hover:scale-105 transition-transform focus:outline-none text-center no-underline";

  if (href) {
    return (
      <Link href={href} className={`${buttonStyle} ${className}`}>
        <span className="block w-full">{children}</span> {/* ✅ Ensures white text & no underline */}
      </Link>
    );
  }

  return (
    <button onClick={onClick} className={`${buttonStyle} ${className}`} type="button">
      {children}
    </button>
  );
};

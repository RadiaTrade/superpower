import React from "react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({ children, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-green-500 text-white font-bold border border-white rounded-xl shadow-md hover:shadow-lg transition-transform hover:scale-105"
    >
      {children}
    </button>
  );
};

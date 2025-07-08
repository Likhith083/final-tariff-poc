import React from "react";
export const Dialog = ({ open, onOpenChange, children }: any) => open ? <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30"><div className="bg-white rounded-lg shadow-lg p-6 min-w-[350px] max-w-[90vw]">{children}<button className="absolute top-2 right-2 text-gray-400 hover:text-gray-700" onClick={() => onOpenChange(false)}>✕</button></div></div> : null;
export const DialogContent = ({ children }: any) => <div>{children}</div>;
export const DialogHeader = ({ children }: any) => <div className="mb-4">{children}</div>;
export const DialogTitle = ({ children }: any) => <h2 className="text-xl font-bold mb-2">{children}</h2>; 
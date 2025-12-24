"use client";
import React from "react";

type Props = {
  onFile: (file: File | null) => void;
};

export default function UploadBox({ onFile }: Props) {
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    onFile(f);
  };

  return (
    <div className="border-2 border-dashed border-[#334155] rounded-xl p-6 text-center bg-slate-800/40 backdrop-blur-md">
      <label className="cursor-pointer flex flex-col items-center justify-center py-6">
        <span className="text-slate-300 mb-2">Click to upload an image</span>
        <span className="text-xs text-slate-500">(JPG, PNG — Max 5MB)</span>
        <input
          type="file"
          accept="image/*"
          onChange={onChange}
          className="hidden"
        />
      </label>
    </div>
  );
}

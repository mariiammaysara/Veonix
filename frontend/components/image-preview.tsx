import React from "react"

type Props = {
  src: string
  alt?: string
}

export default function ImagePreview({ src, alt }: Props) {
  return (
    <div className="mt-4">
      <img
        src={src}
        alt={alt || "preview"}
        className="w-full rounded-xl max-h-72 object-cover border border-[#334155] shadow-lg"
      />
    </div>
  )
}

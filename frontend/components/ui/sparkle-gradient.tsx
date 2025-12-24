export default function SparkleGradient() {
  return (
    <div className="absolute inset-0 -z-10 overflow-hidden">
      <div
        className="absolute w-[500px] h-[500px] rounded-full 
        bg-emerald-500/20 blur-[120px]
        animate-[veonixGradient_12s_ease-in-out_infinite]"
        style={{ top: "-150px", left: "-100px" }}
      ></div>

      <div
        className="absolute w-[400px] h-[400px] rounded-full 
        bg-emerald-400/10 blur-[100px]
        animate-[veonixGradient_15s_ease-in-out_infinite]"
        style={{ bottom: "-150px", right: "-100px" }}
      ></div>
    </div>
  );
}

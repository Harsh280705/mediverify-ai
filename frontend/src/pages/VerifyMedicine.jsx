import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useRef, useState } from "react";

import PageShell from "../components/PageShell";
import PrimaryButton from "../components/PrimaryButton";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";

import { getVerificationSchedule } from "../services/verificationService";
import { processFrame } from "../services/analyticsService";

export default function VerifyMedicine() {
  const { scheduleId } = useParams();
  const navigate = useNavigate();

  const videoRef = useRef(null);
  const mainCanvasRef = useRef(null);
  const motionCanvasRef = useRef(null);
  const prevPixelsRef = useRef(null);

  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Verification States
  const [currentState, setCurrentState] = useState("WAITING");
  const [history, setHistory] = useState(["WAITING"]);
  const [confidence, setConfidence] = useState(0);
  const [summary, setSummary] = useState("");
  const [verifiedSuccess, setVerifiedSuccess] = useState(false);
  const [statusMsg, setStatusMsg] = useState("Aligning camera...");

  // Processing Throttling
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState(0);

  // Detections overlay state (for HUD overlay boxes)
  const [yoloBBoxes, setYoloBBoxes] = useState([]);
  const [handDetected, setHandDetected] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);

  /*
  -------------------------
  Load Schedule
  -------------------------
  */
  useEffect(() => {
    async function loadSchedule() {
      try {
        const data = await getVerificationSchedule(scheduleId);
        setSchedule(data);
        if (data.status === "Taken") {
          setVerifiedSuccess(true);
          setCurrentState("TAKEN");
          setConfidence(100);
          setHistory(["WAITING", "MEDICINE_FOUND", "MATCHED", "HAND_PICKED", "TABLET_NEAR_MOUTH", "TABLET_DISAPPEARED", "MOUTH_CLOSED", "TAKEN"]);
        }
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadSchedule();
  }, [scheduleId]);

  /*
  -------------------------
  Start Camera
  -------------------------
  */
  useEffect(() => {
    let mediaStream;

    async function startCamera() {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "environment",
            width: { ideal: 640 },
            height: { ideal: 480 }
          },
          audio: false
        });

        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error(err);
        alert("Unable to access camera. Please check permissions.");
      }
    }

    if (!verifiedSuccess) {
      startCamera();
    }

    return () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [verifiedSuccess]);

  /*
  -------------------------
  Continuous Capture & Motion Detection Loop
  -------------------------
  */
  useEffect(() => {
    if (loading || error || verifiedSuccess || !schedule) return;

    let active = true;

    async function tick() {
      if (!active) return;

      const video = videoRef.current;
      const motionCanvas = motionCanvasRef.current;
      const mainCanvas = mainCanvasRef.current;

      if (!video || !motionCanvas || !mainCanvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
        requestAnimationFrame(tick);
        return;
      }

      // 1. Client-Side Motion Detection
      const mCtx = motionCanvas.getContext("2d");
      const mw = 40;
      const mh = 30;
      motionCanvas.width = mw;
      motionCanvas.height = mh;

      // Draw small frame
      mCtx.drawImage(video, 0, 0, mw, mh);
      const imgData = mCtx.getImageData(0, 0, mw, mh);
      const pixels = imgData.data;

      let pixelDiff = 0;
      if (prevPixelsRef.current) {
        for (let i = 0; i < pixels.length; i += 4) {
          pixelDiff += Math.abs(pixels[i] - prevPixelsRef.current[i]);     // R
          pixelDiff += Math.abs(pixels[i + 1] - prevPixelsRef.current[i + 1]); // G
          pixelDiff += Math.abs(pixels[i + 2] - prevPixelsRef.current[i + 2]); // B
        }
      }
      prevPixelsRef.current = pixels;

      const avgDiff = pixelDiff / (mw * mh * 3);
      const motionDetected = avgDiff > 9; // Sensitivity threshold (10 is average)

      const now = Date.now();
      const timeElapsed = now - lastCheckTime;

      // Only process if:
      // - Motion is detected AND at least 1000ms has elapsed since last API call OR
      // - Heartbeat fallback (4000ms elapsed since last call to ensure checking anyway)
      const shouldProcess = (motionDetected && timeElapsed > 1200) || timeElapsed > 4500;

      if (shouldProcess && !isProcessing) {
        setIsProcessing(true);
        setLastCheckTime(now);
        setStatusMsg("Analyzing feed...");

        try {
          // Draw high-res frame to main canvas for OCR/Vision
          const ctx = mainCanvas.getContext("2d");
          mainCanvas.width = video.videoWidth;
          mainCanvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, mainCanvas.width, mainCanvas.height);

          // Get base64 string
          const frameBase64 = mainCanvas.toDataURL("image/jpeg", 0.75);

          // Call API
          const result = await processFrame(
            scheduleId,
            frameBase64,
            currentState,
            history,
            confidence
          );

          // Update States
          setCurrentState(result.currentState);
          setHistory(result.history);
          setConfidence(result.confidence);
          setYoloBBoxes(result.yoloDetections || []);
          setHandDetected(result.handDetections?.detected || false);
          setFaceDetected(result.faceDetections?.detected || false);

          if (result.summary) {
            setSummary(result.summary);
          }

          // Handle UI status strings
          if (result.currentState === "TAKEN" || result.statusUpdated) {
            setVerifiedSuccess(true);
            setStatusMsg("Verification complete!");
          } else if (result.currentState === "MOUTH_CLOSED") {
            setStatusMsg("Verification verifying...");
          } else if (result.currentState === "TABLET_DISAPPEARED") {
            setStatusMsg("Tablet swallowed. Close mouth to confirm.");
          } else if (result.currentState === "TABLET_NEAR_MOUTH") {
            setStatusMsg("Take the tablet.");
          } else if (result.currentState === "HAND_PICKED") {
            setStatusMsg("Hold the tablet near your mouth.");
          } else if (result.currentState === "MATCHED") {
            setStatusMsg("Medication matched! Pick a tablet.");
          } else if (result.currentState === "MEDICINE_FOUND") {
            setStatusMsg("Medication detected. Checking name...");
          } else {
            setStatusMsg("Hold the medication in front of the camera.");
          }
        } catch (err) {
          console.error("Frame processing error", err);
          setStatusMsg("Connection issue. Retrying...");
        } finally {
          setIsProcessing(false);
        }
      }

      // Loop
      setTimeout(() => {
        requestAnimationFrame(tick);
      }, 200);
    }

    requestAnimationFrame(tick);

    return () => {
      active = false;
    };
  }, [loading, error, verifiedSuccess, schedule, currentState, history, confidence, isProcessing, lastCheckTime]);

  /*
  -------------------------
  Verification Success Hook (Auto-redirect)
  -------------------------
  */
  useEffect(() => {
    if (verifiedSuccess) {
      const timer = setTimeout(() => {
        navigate("/patient");
      }, 3500);
      return () => clearTimeout(timer);
    }
  }, [verifiedSuccess, navigate]);

  if (loading) {
    return (
      <PageShell eyebrow="Medicine Verification" title="Loading..." description="Fetching today's medication.">
        <p className="text-slate-400">Please wait while we load details...</p>
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell eyebrow="Medicine Verification" title="Error" description={error}>
        <PrimaryButton onClick={() => navigate(-1)}>Go Back</PrimaryButton>
      </PageShell>
    );
  }

  const checklistItems = [
    { key: "MEDICINE_FOUND", label: "Medicine Detected (20%)" },
    { key: "MATCHED", label: "Medicine Matched (20%)" },
    { key: "HAND_PICKED", label: "Hand Picked Dosing (15%)" },
    { key: "TABLET_NEAR_MOUTH", label: "Tablet Approaching Mouth (15%)" },
    { key: "TABLET_DISAPPEARED", label: "Tablet Swallowed (15%)" },
    { key: "MOUTH_CLOSED", label: "Mouth Closed (15%)" }
  ];

  return (
    <PageShell
      eyebrow="AI Assist Mode"
      title="Verify Medication"
      description="Hold the prescribed medicine strip or bottle in front of the camera. The AI will verify compliance automatically."
    >
      {/* Verification Success Full-Screen Overlay */}
      {verifiedSuccess && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-950/85 backdrop-blur-md transition-all duration-500">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-5xl animate-bounce">
            ✓
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-white">Dose Verified Successfully!</h2>
          <p className="mt-2 text-sm text-slate-400">Updating schedule status to Taken...</p>
          <p className="mt-1 text-xs text-indigo-300 font-semibold">Redirecting to Dashboard in 3s</p>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Expected Medication Details */}
        <div className="lg:col-span-1 space-y-6">
          <SectionCard title="Dose to Take">
            <div className="space-y-3 text-sm text-slate-200">
              <p>
                <strong>Medication:</strong> <span className="text-white font-semibold">{schedule.medicineName}</span>
              </p>
              <p>
                <strong>Strength:</strong> {schedule.strength || "-"}
              </p>
              <p>
                <strong>Dosage:</strong> {schedule.dosage || "-"}
              </p>
              <p>
                <strong>Instructions:</strong> {schedule.instructions || "-"}
              </p>
              <p>
                <strong>Timing:</strong> {schedule.timing || "-"}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                <span className="rounded-full bg-cyan-500/10 text-cyan-300 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider">
                  {schedule.status}
                </span>
              </p>
            </div>
          </SectionCard>

          {/* Adherence State Machine HUD checklist */}
          <SectionCard title="Adherence Verification Steps">
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Confidence Tracker</span>
                <span className="font-semibold text-white">{confidence}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-indigo-500 transition-all duration-300"
                  style={{ width: `${confidence}%` }}
                ></div>
              </div>
              
              <div className="mt-4 space-y-2.5">
                {checklistItems.map((item) => {
                  const completed = history.includes(item.key);
                  return (
                    <div key={item.key} className="flex items-center gap-3 text-sm transition">
                      <span className={`text-base ${completed ? "text-emerald-400" : "text-slate-600"}`}>
                        {completed ? "●" : "○"}
                      </span>
                      <span className={completed ? "text-white font-medium" : "text-slate-500"}>
                        {item.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Live Video Camera Overlay */}
        <div className="lg:col-span-2 space-y-6">
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-black aspect-video w-full shadow-lg">
            
            {/* Pulsing overlay boundary */}
            <div className="absolute inset-0 z-10 border-4 border-cyan-400/20 pointer-events-none rounded-2xl"></div>

            {/* Google Lens Scan line effect */}
            <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-60 animate-[pulse_2s_infinite] pointer-events-none z-10" style={{
              top: '40%',
              animation: 'scanLine 3s linear infinite'
            }}></div>

            {/* Target dots in center */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center z-10 pointer-events-none">
              <div className="h-16 w-16 rounded-full border-2 border-dashed border-cyan-400/40 animate-spin"></div>
              <div className="absolute h-4 w-4 rounded-full bg-cyan-400/30 animate-ping"></div>
            </div>

            {/* Status floating overlay info */}
            <div className="absolute top-4 left-4 z-20 rounded-xl bg-slate-950/80 backdrop-blur-md border border-white/10 px-3 py-1.5 text-xs text-cyan-300 font-semibold tracking-wide animate-pulse">
              {statusMsg.toUpperCase()}
            </div>

            {/* Mini landmarks status floating overlays */}
            <div className="absolute top-4 right-4 z-20 flex gap-2">
              <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold ${handDetected ? "bg-emerald-500/20 text-emerald-300" : "bg-white/5 text-slate-500"}`}>
                🖐 HAND
              </span>
              <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold ${faceDetected ? "bg-indigo-500/20 text-indigo-300" : "bg-white/5 text-slate-500"}`}>
                👤 FACE
              </span>
            </div>

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="h-full w-full object-cover rounded-2xl"
            />

            {/* Hidden Canvases */}
            <canvas ref={mainCanvasRef} className="hidden" />
            <canvas ref={motionCanvasRef} className="hidden" />
          </div>

          {/* AI generated Medication Info sliding card */}
          {summary && (
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md p-6 relative overflow-hidden transition-all duration-500 hover:border-cyan-500/30">
              <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-cyan-400 to-indigo-500"></div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-300">
                💡 AI Medication Guide (Ollama Summarizer)
              </h3>
              <p className="mt-3 text-sm text-slate-200 whitespace-pre-line leading-relaxed font-medium">
                {summary}
              </p>
            </div>
          )}

          <div className="flex justify-between items-center bg-white/5 border border-white/10 rounded-2xl p-4">
            <span className="text-xs text-slate-400">Verifying session: {scheduleId}</span>
            <button
              onClick={() => navigate(-1)}
              className="text-sm font-semibold text-slate-300 underline hover:text-white"
            >
              Cancel Verification
            </button>
          </div>
        </div>
      </div>
      
      {/* Scan line animation definition */}
      <style>{`
        @keyframes scanLine {
          0% { top: 0%; }
          50% { top: 100%; }
          100% { top: 0%; }
        }
      `}</style>
    </PageShell>
  );
}
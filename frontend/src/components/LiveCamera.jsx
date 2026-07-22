import { useEffect, useRef, useState } from "react";

export default function LiveCamera() {

    const videoRef = useRef(null);

    const streamRef = useRef(null);

    const [error, setError] = useState("");

    const canvasRef = useRef(null);

    function captureFrame() {

    if (
        !videoRef.current ||
        !canvasRef.current
    )
        return;

    const video = videoRef.current;

    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;

    canvas.height = video.videoHeight;

    const ctx =
        canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0
    );

    console.log(
    "Frame captured",
    new Date().toLocaleTimeString()
);

}
    useEffect(() => {

        async function startCamera() {

            try {

                const stream =
                    await navigator.mediaDevices.getUserMedia({

                        video: {

                            facingMode: "environment",

                            width: { ideal: 1280 },

                            height: { ideal: 720 }

                        },

                        audio: false,

                    });

                streamRef.current = stream;

                if (videoRef.current) {

                    videoRef.current.srcObject = stream;

                    videoRef.current.onloadedmetadata = () => {

                        videoRef.current.play();

                    };

                }

            }

            catch {

                setError("Unable to access camera.");

            }

        }

        startCamera();
        const interval = setInterval(() => {

        captureFrame();

        }, 1000);

        return () => {

        clearInterval(interval);

        if (streamRef.current) {

            streamRef.current
                .getTracks()
                .forEach(track => track.stop());

        }
    };

    }, []);

    if (error)
        return <p>{error}</p>;

    return (

        <div className="rounded-xl overflow-hidden shadow-lg">

            <video

                ref={videoRef}

                autoPlay

                muted

                playsInline

                className="w-full rounded-xl"
                
            />
            <canvas

            ref={canvasRef}

            style={{ display: "none" }}

            />

        </div>

    );

}
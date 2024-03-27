import React, { useState, useRef, useEffect } from "react";
import { MediaRecorder, register } from "extendable-media-recorder";
import { connect } from "extendable-media-recorder-wav-encoder";

const App = () => {
  const [serverAddress, setServerAddress] = useState("ws://192.168.1.8:8000");
  const [isRecording, setIsRecording] = useState(false);
  // Use an array to hold individual transcription messages
  const [transcriptionMessages, setTranscriptionMessages] = useState([]);
  const mediaRecorderRef = useRef(null);
  const websocketRef = useRef(null);
  const transcriptionContainerRef = useRef(null);

  useEffect(() => {
    const setup = async () => {
      try {
        await register(await connect());
      } catch (error) {
        console.error(error);
      }
    };
    setup();
  }, []);

  // Scroll to the bottom of the transcription container whenever transcriptionMessages updates
  useEffect(() => {
    if (transcriptionContainerRef.current) {
      transcriptionContainerRef.current.scrollTop =
        transcriptionContainerRef.current.scrollHeight;
    }
  }, [transcriptionMessages]);

  const startRecording = async () => {
    setTranscriptionMessages([]);
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContext({ sampleRate: 16000 });
      const sourceNode = audioContext.createMediaStreamSource(stream);
      const destinationNode = audioContext.createMediaStreamDestination();
      sourceNode.connect(destinationNode);

      const mediaRecorder = new MediaRecorder(destinationNode.stream, {
        mimeType: "audio/wav",
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.onstart = () => {
        websocketRef.current = new WebSocket(`${serverAddress}/${uuidv4()}`);
        setIsRecording(true);
      };

      mediaRecorder.ondataavailable = async (event) => {
        if (
          event.data.size > 0 &&
          websocketRef.current &&
          websocketRef.current.readyState === WebSocket.OPEN
        ) {
          const arrayBuffer = await event.data.arrayBuffer();
          websocketRef.current.send(arrayBuffer);
          websocketRef.current.onmessage = (message) => {
            if (message.data !== " ") {
              setTranscriptionMessages((prevMessages) => [
                ...prevMessages,
                { text: message.data, isNew: true }, // Mark new messages as 'isNew'
              ]);

              // Reset the 'isNew' flag after a delay, if desired
              setTimeout(() => {
                setTranscriptionMessages((prevMessages) =>
                  prevMessages.map((msg) => ({ ...msg, isNew: false }))
                );
              }, 3000); // For example, after 3 seconds
            }
          };
        }
      };

      mediaRecorder.start(1000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const uuidv4 = () => {
    return "xxxx-xxxx-4xxx-yxxx-xxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0,
        v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        height: "100vh",
        width: "100vw",
      }}
    >
      <h1>Audio Transcription</h1>
      <input
        type="text"
        value={serverAddress}
        onChange={(e) => setServerAddress(e.target.value)}
        placeholder="Enter Server Address"
        style={{
          height: "50px",
          width: "400px",
          textAlign: "center",
          padding: "10px",
          fontSize: "30px",
        }}
      />
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? "Stop" : "Start"} Recording
      </button>
      <div
        ref={transcriptionContainerRef}
        style={{
          marginTop: "20px",
          width: "800px",
          height: "500px",
          overflowY: "scroll",
          fontSize: "20px",
          padding: "10px",
          border: "1px solid #ccc",
          borderRadius: "5px",
          backgroundColor: "#f9f9f9",
        }}
      >
        {transcriptionMessages.map((message, index) => (
          <span
            key={index}
            style={{
              color: message.isNew ? "#ff0000" : "#000000", // Change color for new messages
              marginBottom: "5px",
            }}
          >
            {message.text}
          </span>
        ))}
      </div>
    </div>
  );
};

export default App;

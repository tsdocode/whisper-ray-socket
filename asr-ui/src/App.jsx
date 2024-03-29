import { useState, useRef, useEffect } from "react";
import { MediaRecorder, register } from "extendable-media-recorder";
import { connect } from "extendable-media-recorder-wav-encoder";

const App = () => {
  const [serverAddress, setServerAddress] = useState(
    "wss://asr.tsdocode.online"
  );
  const [isRecording, setIsRecording] = useState(false);
  // Use an array to hold individual transcription messages
  const [transcriptionMessages, setTranscriptionMessages] = useState([]);
  const mediaRecorderRef = useRef(null);
  const websocketRef = useRef(null);
  const [channels, setChannels] = useState(1);

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

          let metaChannels;

          if (
            arrayBuffer.byteLength % 16000 == 0 ||
            arrayBuffer.byteLength - (44 % 16000) == 0
          ) {
            const apxChannels = arrayBuffer.byteLength / 2 / 16000 / 1;
            console.log(apxChannels);


            setChannels(() => Math.floor(apxChannels));

            metaChannels = apxChannels;
          } else {
            metaChannels = channels;
          }

          console.log(metaChannels);

          const metadata = {
            samplewidth: 2,
            framerate: 16000,
            channels: metaChannels,
          };

          websocketRef.current.send(JSON.stringify(metadata));
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
      <h1 style={{}}>Whisper Realtime with Websocket</h1>

      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          value={serverAddress}
          onChange={(e) => setServerAddress(e.target.value)}
          placeholder="Enter Server Address"
          style={{
            height: "30px",
            width: "80%",
            textAlign: "center",
            padding: "10px",
            fontSize: "30px",
            borderColor: "blue",
            marginLeft: "10px",
          }}
        />
        <button
          onClick={isRecording ? stopRecording : startRecording}
          style={{
            height: "60px",
            padding: "10px",
          }}
        >
          {isRecording ? "Stop" : "Start"} Recording
        </button>
      </div>

      <div
        ref={transcriptionContainerRef}
        style={{
          marginTop: "20px",
          width: "90%",
          height: "45%",
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

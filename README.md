# Realtime ASR System Example

[![IMAGE ALT TEXT HERE](./assets/demo.gif)](https://youtu.be/aTMmpaFe1h0)

> Serving on my GTX 1050ti Laptop, Click on gif watch youtube video

> [!IMPORTANT]
> Demo is online at https://tsdocode.github.io/whisper-ray-socket/


> [!IMPORTANT]
> This repository is my practice on training and serving a realtime Automatic Speech Recognition (ASR) System.




##### Table of Contents  
[1. Introduction](#1-introduction)  
[2. Training](#2-training)  
[3. Serving](#3-serving)  
[4. Improvement](#4-improvement)  
[5. References](#5-references)  

## 1. Introduction
In the digital era, Automatic Speech Recognition (ASR) systems have become ubiquitous, with well-known examples including Google's Text-to-Speech, IBM Watson, and Amazon Polly. However, this repository focuses on self-hosted models, specifically OpenAI's Whisper and its distilled version, Distil Whisper. These models offer a promising avenue for those looking to deploy powerful ASR systems within their own infrastructure.

This repo will cover the basics of the Whisper and Distil Whisper models, including how to fine-tune Distil Whisper using Accelerate and optimize its hyperparameters. We'll also explore how to convert the model to a faster version suitable for real-time applications and discuss the process of uploading the final model to Hugging Face for easy access and deployment.

## 2. Serving

Deploying an ASR system in a real-time environment requires careful consideration of latency, scalability, and reliability. This section will focus on using WebSockets for real-time audio processing and how to manage audio streams effectively.

![serving_overview](./assets/serving_flow.png)

Flow:
- User (client) send audio buffer (recorded from mic) via websocket in arrayBuffer format each 1s
- Websocket server receives buffer and starts async process
- Buffer manager merges with existed buffer of the client and runs VAD on merge buffer and trim buffer based on VAD result 
- Buffer manager returns buffer to asr (buffer which has voice activity)
- Do speech recognition with this buffer, then send the transcribed message back to the user

### 2.1 Buffer Management Method
Managing audio buffers efficiently is crucial for minimizing latency in real-time ASR systems. This subsection will discuss strategies for buffer management and how to ensure seamless audio processing.

![](./assets/buffer_flow.png)

### 2.2 Deployment
This part will cover the deployment process, including server setup, WebSocket configuration, and ensuring your ASR system is scalable and reliable.

The whole websocket system and deploy using Ray serve in a ray cluster

Step to run:
1. Start a Ray cluster (skip if you already have)
```
pip install -r requirements.txt
ray start --head
```

2. Serve all deployments

```
cd serve
serve deploy serve.yaml
```

Websocket will be locate at ws://0.0.0.0:8000

## 3. Improvement
- Merge result of chunks for better context
- whisper.cpp ?
- Continuous batching for better through put
- ...

## 4. References

1. [Whisper Live](https://github.com/collabora/WhisperLive)
2. [Streaming Whisper](https://github.com/ufal/whisper_streaming)


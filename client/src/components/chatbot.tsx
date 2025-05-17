import { useRef, useState } from "react"
import {
	useMessages,
	sendChatbotText,
	sendChatbotAudio,
	type Message,
} from "../api/chat"
import { API_URL } from "../api/api"

export default function Chatbot({
	studentId,
	programId,
	language,
}: {
	studentId: number
	programId: number
	language: string
}) {
	const [input, setInput] = useState("")
	const [recording, setRecording] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const [loading, setLoading] = useState(false)
	const mediaRecorderRef = useRef<MediaRecorder | null>(null)
	const audioChunks = useRef<BlobPart[]>([])

	const { data: messages, isLoading } = useMessages(programId, studentId, 2000)

	// Find the last bot message for reply/audio
	const lastBotMsg = messages
		? [...messages].reverse().find((msg) => msg.from === "bot")
		: undefined

	const audioReply =
		lastBotMsg && lastBotMsg.audio_link?.startsWith("media/")
			? lastBotMsg.audio_link
			: null

	const audioKey = audioReply
	const audioUrl = audioReply ? API_URL + "/audio/" + audioReply : undefined

	// Send text message
	const handleSendText = async () => {
		if (!input.trim()) return
		setLoading(true)
		setError(null)
		try {
			const res = await sendChatbotText({
				text: input,
				user_id: studentId,
				program_id: programId,
				language,
			})
			setLoading(false)
			if (!res.ok) {
				setError(res.error || "Failed to send message")
			} else {
				setInput("")
			}
		} catch {
			setLoading(false)
			setError("Failed to send message")
		}
	}

	// Send audio message
	const handleSendAudio = async (audioFile: File) => {
		setLoading(true)
		setError(null)
		try {
			const res = await sendChatbotAudio({
				audio: audioFile,
				user_id: studentId,
				program_id: programId,
				language,
			})
			setLoading(false)
			if (!res.ok) {
				setError(res.error || "Failed to send audio")
			}
		} catch {
			setLoading(false)
			setError("Failed to send audio")
		}
	}

	// Microphone recording logic
	const startRecording = async () => {
		setRecording(true)
		setError(null)
		audioChunks.current = []
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
			const mediaRecorder = new window.MediaRecorder(stream, {
				mimeType: "audio/webm",
			})
			mediaRecorderRef.current = mediaRecorder

			mediaRecorder.ondataavailable = (e) => {
				audioChunks.current.push(e.data)
			}
			mediaRecorder.onstop = () => {
				const blob = new Blob(audioChunks.current, { type: "audio/webm" })
				const file = new File([blob], "recording.webm", { type: "audio/webm" })
				handleSendAudio(file)
				setRecording(false)
			}
			mediaRecorder.start()
			setTimeout(() => {
				mediaRecorder.stop()
			}, 4000) // Record for 4 seconds
		} catch {
			setError("Microphone access denied or not available")
			setRecording(false)
		}
	}

	return (
		<div className="flex flex-col gap-4 w-full bg-white rounded-sm shadow-sm p-4 border border-gray-200">
			<h2 className="text-xl font-bold mb-2">Chatbot</h2>
			<div
				className="flex flex-col gap-2 h-64 overflow-y-auto rounded p-2"
				ref={(el) => {
					if (el) el.scrollTop = el.scrollHeight
				}}
			>
				{isLoading && <div className="text-gray-400">Loading messages...</div>}
				{messages?.map((msg: Message, idx: number) => (
					<div
						key={msg.id || idx}
						className={`flex flex-col ${
							msg.from === "bot" ? "items-start" : "items-end"
						}`}
					>
						<span className="text-xs text-gray-400 mb-1">
							{msg.from === "bot" ? "Bot" : "You"}
						</span>
						<div
							className={`px-3 py-2 rounded ${
								msg.from === "bot"
									? "bg-blue-50 text-black"
									: "bg-gray-200 text-gray-800"
							}`}
						>
							{msg.content.startsWith("temp/") ? (
								<span className="uppercase text-gray-600 font-bold text-sm">
									Audio Message
								</span>
							) : (
								msg.content
							)}
							{audioUrl && audioReply === msg.audio_link && (
								<div className="flex flex-col gap-2 mt-4">
									<audio key={audioKey} controls>
										<source src={audioUrl} type="audio/mpeg" />
										Your browser does not support the audio element.
									</audio>
									<p className="text-sm">
										Click the play button to listen to the explanation!
									</p>
								</div>
							)}
						</div>
					</div>
				))}
			</div>
			<div className="flex flex-row gap-2 items-center">
				<input
					type="text"
					className="flex-1 border rounded px-3 py-2"
					placeholder="Type your question..."
					value={input}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={(e) => {
						if (e.key === "Enter") handleSendText()
					}}
					disabled={loading}
				/>
				<button
					onClick={handleSendText}
					disabled={loading || !input.trim()}
					className="bg-blue-500 text-white px-4 py-2 rounded font-semibold shadow-sm hover:bg-blue-600 transition"
				>
					{loading ? "Sending..." : "Send"}
				</button>
				<button
					onClick={startRecording}
					disabled={recording || loading}
					className={`border border-blue-500 text-blue-800 px-4 py-2 rounded font-semibold shadow-sm hover:bg-blue-600 hover:text-white transition ${
						recording ? "opacity-50" : ""
					}`}
				>
					{recording ? "Recording..." : "Record 🎤"}
				</button>
			</div>
			{/* {(botReply || audioUrl) && (
				<div className="mt-2 flex flex-col gap-2">
					{botReply && (
						<div className="">
							<b>Bot</b> {botReply}
						</div>
					)}
					{audioUrl && (
						<div className="flex flex-col gap-2 p-4 border border-gray-200 rounded-md">
							<audio key={audioKey} controls>
								<source src={audioUrl} type="audio/mpeg" />
								Your browser does not support the audio element.
							</audio>
							<p className="text-sm">
								Click the play button to listen to the explanation!
							</p>
						</div>
					)}
				</div>
			)} */}
			{error && <div className="text-red-500">{error}</div>}
		</div>
	)
}

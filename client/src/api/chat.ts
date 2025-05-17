import useSWR from "swr"
import { API, axiosErrorHandler } from "./api"

export interface Message {
	id: number
	program_id: number
	user_id: number | null
	audio_link?: string | null
	content: string
	from: string
	sent_at: string
}

export interface ChatbotTextRequest {
	text: string
	language?: string
	user_id: number
	program_id: number
}

export interface ChatbotAudioRequest {
	audio: File
	language?: string
	user_id: number
	program_id: number
}

export interface ChatbotResponse {
	user_text: string
	bot_reply: string
	audio_reply_path: string
}

export function useMessages(
	program_id: number,
	user_id: number,
	refreshInterval = 2000
) {
	return useSWR<Message[]>(
		program_id && user_id
			? `/chat/messages?program_id=${program_id}&user_id=${user_id}`
			: null,
		(url) => API.get(url).then((res) => res.data),
		{ refreshInterval }
	)
}

// Send a text message to the chatbot
export const sendChatbotText = async (input: ChatbotTextRequest) => {
	const form = new FormData()
	form.append("text", input.text)
	form.append("user_id", input.user_id.toString())
	form.append("program_id", input.program_id.toString())
	if (input.language) form.append("language", input.language)
	return axiosErrorHandler(() => API.post("/chat/message", form))
}

// Send an audio file to the chatbot
export const sendChatbotAudio = async (input: ChatbotAudioRequest) => {
	const form = new FormData()
	form.append("audio", input.audio)
	form.append("user_id", input.user_id.toString())
	form.append("program_id", input.program_id.toString())
	if (input.language) form.append("language", input.language)
	return axiosErrorHandler(() => API.post("/chat/message", form))
}

/* eslint-disable @typescript-eslint/no-explicit-any */
import useSWR from "swr"
import { fetcher, API, axiosErrorHandler } from "./api"

// --- Types ---
export interface Program {
	id: number
	title: string
	description: string
	code: string
	class_id: number
}

export interface TestCase {
	input: any[]
	output: any[]
}

export interface Summary {
	id: number
	program_id: number
	audio_link?: string
	language: string
	summary: string
	test_cases?: TestCase[]
	algorithm?: string // Added: optional algorithm field
}

export interface ProgramDetail {
	program: Program
	summaries: Summary[]
}

export interface Message {
	id: number
	program_id: number
	user_id: number | null
	content: string
	from: string
	sent_at: string
}

export interface Language {
	code: string
	name: string
	classroom_id: number
}

// --- SWR Hooks ---

// Get all programs
export function usePrograms() {
	return useSWR<Program[]>("/programs", fetcher)
}

// Get a single program and its summaries
export function useProgramDetail(id: number | string | undefined) {
	return useSWR<ProgramDetail>(id ? `/programs/${id}` : null, fetcher)
}

// Get programs by classroom
export function useProgramsByClass(classId: number | string | undefined) {
	return useSWR<Program[]>(
		classId ? `/programs/classroom/${classId}` : null,
		fetcher
	)
}

// --- Mutations ---

// Create a new program
export async function createProgram(input: {
	title: string
	description: string
	code: string
	class_id: number
}) {
	return axiosErrorHandler(() => API.post("/programs", input))
}

// Delete a program
export async function deleteProgram(id: number) {
	if (id === 0) return

	return axiosErrorHandler(() => API.delete(`/programs/${id}`))
}

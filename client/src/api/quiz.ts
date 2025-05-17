import useSWR from "swr"
import { API, axiosErrorHandler, fetcher } from "./api"

// Types for quiz submission and response
export interface QuizSubmissionInput {
	program_id: number
	user_id: number
	code: string
	language_id: number
	quiz_language?: string
}

export interface QuizSubmissionResult {
	id: number
	results: {
		stdin: string
		stdout: string
		stderr: string
		compile_output: string
	}[]
	quiz: {
		code_correct: boolean
		code_errors: {
			error_type: string
			description: string
			incorrect_code: string
			correct_code: string
		}[]
		quiz: {
			question: string
			options: string[]
		}[]
	}
	quiz_id: number
}

export interface Quiz {
	id: number
	student_id: number
	program_id: number
	class_id?: number
	questions: {
		question: string
		options: string[]
	}[]
	answers: { [key: string]: string }
	marks: number
}

export interface MarkQuizInput {
	quiz_id: number
	answers: Record<string, string>
}

// --- API Calls ---

// Submit code and get quiz
export async function submitQuiz(input: QuizSubmissionInput) {
	return axiosErrorHandler(() =>
		API.post<QuizSubmissionResult>("/submissions", input)
	)
}

// Mark answers for a quiz
export async function markQuizAnswers(input: MarkQuizInput) {
	return axiosErrorHandler(() => API.post("/quiz/mark", input))
}

// --- SWR Hooks ---

// Get quiz by program and user id
export function useQuizByProgramUser(programId?: number, userId?: number) {
	return useSWR<Quiz>(
		programId && userId ? `/quiz/program/${programId}/user/${userId}` : null,
		fetcher
	)
}

// Get quizzes by class
export function useQuizzesByClass(classId?: number) {
	return useSWR<Quiz[]>(classId ? `/quiz/class/${classId}` : null, fetcher)
}

// Get quizzes by program
export function useQuizzesByProgram(
	programId?: number,
	role: string = "student"
) {
	return useSWR<Quiz[]>(
		programId && role === "professor" ? `/quiz/program/${programId}` : null,
		fetcher
	)
}

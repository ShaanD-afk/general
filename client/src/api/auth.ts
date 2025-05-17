import { navigate } from "wouter/use-browser-location"
import { useAuth } from "../state/auth"
import { API, axiosErrorHandler } from "./api"

interface RegisterInput {
	username: string
	password: string
	role: string
	class_id?: number
}

interface LoginInput {
	username: string
	password: string
}

interface User {
	id: number
	username: string
	role: string
	class_id?: number
}

interface ApiResponse<T> {
	error: string | null
	ok: boolean
	data: T | null
	blob: null // Not used here
}

// --- REGISTER ---
export const registerUser = async (
	input: RegisterInput
): Promise<ApiResponse<{ user_id: number }>> => {
	return axiosErrorHandler(() => API.post("/register", input))
}

// --- LOGIN ---
export const loginUser = async (
	input: LoginInput
): Promise<ApiResponse<{ message: string }>> => {
	return axiosErrorHandler(() => API.post("/login", input))
}

// --- LOGOUT ---
export const logoutUser = async (): Promise<
	ApiResponse<{ message: string }>
> => {
	useAuth.getState().logout()
	const res = await axiosErrorHandler(() => API.post("/logout"))

	if (res.ok) navigate("/")

	return res
}

// --- GET CURRENT USER ---
export const getCurrentUser = async (): Promise<ApiResponse<User>> => {
	return axiosErrorHandler(() => API.get("/me"))
}

import { create } from "zustand"

interface User {
	id: number
	username: string
	role: string
}

interface AuthState {
	user: User | null
	login: (user: User) => void
	logout: () => void
	isAuthenticated: () => boolean
}

export const useAuth = create<AuthState>(
	(set: (x: Partial<AuthState>) => void, get: () => AuthState) => ({
		user: null,

		login: (user: User) => set({ user }),

		logout: () => set({ user: null }),

		isAuthenticated: () => get().user !== null,
	})
)

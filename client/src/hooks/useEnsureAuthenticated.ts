import { useEffect } from "react"
import { useLocation } from "wouter"
import { getCurrentUser } from "../api/auth"
import { useAuth } from "../state/auth" // adjust path if needed

export function useEnsureAuthenticated(shouldBeAuthenticated: boolean) {
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	const [_, navigate] = useLocation()
	const user = useAuth((state) => state.user)
	const login = useAuth((state) => state.login)
	const logout = useAuth((state) => state.logout)

	useEffect(() => {
		const checkAuth = async () => {
			// // Already known state
			// if (user) {
			// 	if (!shouldBeAuthenticated) navigate("/home")
			// 	return
			// }

			const res = await getCurrentUser()

			if (res.ok && res.data) {
				login(res.data)
				if (!shouldBeAuthenticated) {
					navigate("/home")
				}
			} else {
				logout()
				if (shouldBeAuthenticated) {
					navigate("/login")
				}
			}
		}

		checkAuth()
	}, [shouldBeAuthenticated, login, logout, navigate])

	return user
}

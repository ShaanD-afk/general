import { useEffect } from "react"
import { useLocation } from "wouter"

export default function IndexPage() {
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	const [_, navigate] = useLocation()

	useEffect(() => {
		navigate("/login")
	}, [navigate])

	return <></>
}

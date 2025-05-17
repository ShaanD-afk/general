/* eslint-disable @typescript-eslint/ban-ts-comment */
import axios from "axios"

export const API_URL =
	import.meta.env.VITE_API_URL || "http://100.107.65.96:5051/"

export const API = axios.create({
	baseURL: API_URL,
	withCredentials: true,
})

export const fetcher = (url: string) =>
	API.get(url, {
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
	}).then((res) => res.data)

export const axiosErrorHandler = async (
	// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
	fn: Function,
	isBlob: boolean = false
) => {
	try {
		const res = await fn()

		if (res.status < 300 && res.status > 199) {
			return {
				error: null,
				ok: true,
				data: isBlob ? res.data : res.data,
				blob: isBlob ? res.data : null,
			}
		} else {
			return {
				error: res.data?.message ?? res.statusText,
				ok: false,
				data: null,
				blob: null,
			}
		}
	} catch (e: unknown) {
		return {
			error:
				typeof e === typeof Error()
					? // @ts-ignore
					  e.response?.data?.cause?.message ?? e.message
					: JSON.stringify(e),
			ok: false,
			data: null,
			blob: null,
		}
	}
}

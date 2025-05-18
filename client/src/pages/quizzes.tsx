import { useQuizzesByUser } from "../api/quiz"
import { useEnsureAuthenticated } from "../hooks/useEnsureAuthenticated"

export default function QuizzesPage() {
	const user = useEnsureAuthenticated(true)
	const { data: quizzes, isLoading } = useQuizzesByUser(user?.id ?? 0)

	if (isLoading) return <p className="p-4">Loading...</p>

	console.log(quizzes)

	return (
		<div className="flex flex-col gap-4 p-4">
			<h1 className="text-2xl font-bold">Quiz History</h1>
			{(quizzes ?? []).map((quiz) => (
				<div className="flex flex-row w-full justify-between">
					<h2 className="text-xl font-bold">
						{quiz.program_name ?? "Unknown Program"}
					</h2>
					<p className="text-xl font-light">
						{quiz.marks} / {quiz.questions.length}
					</p>
				</div>
			))}
		</div>
	)
}

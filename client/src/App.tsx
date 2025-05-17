import { Route, Switch, useLocation } from "wouter"
import HomePage from "./pages/home"
import LoginPage from "./pages/login"
import IndexPage from "./pages"
import Header from "./components/header"
import NewProgramPage from "./pages/newProgram"
import ProgramPage from "./pages/program"
import QuizPage from "./pages/quiz"

function App() {
	const [location] = useLocation()

	return (
		<main className="w-screen h-screen bg-gray-50 flex flex-col">
			{location !== "/login" ? <Header /> : <></>}
			<Switch>
				<Route path="/" component={IndexPage} />
				<Route path="/home" component={HomePage} />
				<Route path="/login" component={LoginPage} />
				<Route path="/program/new" component={NewProgramPage} />
				<Route path="/program/:id" component={ProgramPage} />
				<Route path="/program/:programId/quiz" component={QuizPage} />
			</Switch>
		</main>
	)
}

export default App

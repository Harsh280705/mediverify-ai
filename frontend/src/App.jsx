import AppRouter from "./routes/AppRouter";
import ReminderScheduler from "./components/ReminderScheduler";

export default function App() {
  return (
    <>
      <ReminderScheduler />
      <AppRouter />
    </>
  );
}
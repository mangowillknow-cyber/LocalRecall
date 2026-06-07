import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { SearchPage } from './pages/SearchPage';
import { FilesPage } from './pages/FilesPage';
import { TagsPage } from './pages/TagsPage';
import { StatusPage } from './pages/StatusPage';
import { SettingsPage } from './pages/SettingsPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100">
        <Sidebar />
        <main className="flex-1 flex flex-col overflow-hidden">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/files" element={<FilesPage />} />
            <Route path="/tags" element={<TagsPage />} />
            <Route path="/status" element={<StatusPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

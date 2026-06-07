import { useState, useEffect } from 'react';

export function SettingsPage() {
  const [settings, setSettings] = useState<any>({});
  const [dirPath, setDirPath] = useState('');

  useEffect(() => {
    fetch('/api/settings').then(r => r.json()).then(setSettings).catch(() => {});
  }, []);

  const save = async () => {
    await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
  };

  const addDir = async () => {
    if (!dirPath.trim()) return;
    const res = await fetch('/api/index/directory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: dirPath.trim() }),
    });
    const data = await res.json();
    alert(JSON.stringify(data, null, 2));
    setDirPath('');
  };

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-xl font-semibold mb-6">设置</h1>

      <section className="mb-8">
        <h2 className="text-lg font-medium mb-3">数据源</h2>
        <p className="text-sm text-zinc-500 mb-3">添加要索引的本地目录</p>
        <div className="flex gap-2">
          <input
            value={dirPath}
            onChange={e => setDirPath(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addDir()}
            placeholder="/path/to/your/notes"
            className="flex-1 px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-transparent text-sm"
          />
          <button onClick={addDir} className="px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg text-sm font-medium cursor-pointer">添加</button>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-lg font-medium mb-3">LLM 配置</h2>
        <label className="block mb-1.5 text-sm text-zinc-500">Ollama 地址</label>
        <input
          value={settings.ollama_url || ''}
          onChange={e => setSettings({ ...settings, ollama_url: e.target.value })}
          className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-transparent text-sm mb-4"
        />
        <label className="block mb-1.5 text-sm text-zinc-500">模型名称</label>
        <input
          value={settings.ollama_model || ''}
          onChange={e => setSettings({ ...settings, ollama_model: e.target.value })}
          className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-transparent text-sm mb-4"
        />
        <button onClick={save} className="px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg text-sm font-medium cursor-pointer">保存</button>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">主题</h2>
        <select
          value={settings.theme || 'system'}
          onChange={e => {
            setSettings({ ...settings, theme: e.target.value });
            const root = document.documentElement;
            if (e.target.value === 'dark' || (e.target.value === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
              root.classList.add('dark');
            } else {
              root.classList.remove('dark');
            }
          }}
          className="px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-transparent text-sm"
        >
          <option value="light">浅色</option>
          <option value="dark">深色</option>
          <option value="system">跟随系统</option>
        </select>
      </section>
    </div>
  );
}

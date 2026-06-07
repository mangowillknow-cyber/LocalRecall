import { useState, useEffect } from 'react';

export function FilesPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch('/api/index/stats').then(r => r.json()).then(setStats).catch(() => {});
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-6">已索引文件</h1>
      {stats ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="总文件" value={stats.total_files} />
          <StatCard label="向量块" value={stats.total_chunks} />
          <StatCard label="已索引" value={stats.indexed} />
          <StatCard label="错误" value={stats.errors} />
        </div>
      ) : (
        <p className="text-zinc-400 text-sm">加载中...</p>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
      <div className="text-2xl font-bold">{value?.toLocaleString() ?? 0}</div>
      <div className="text-sm text-zinc-500">{label}</div>
    </div>
  );
}

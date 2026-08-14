import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './Dashboard';

const queryClient = new QueryClient();   // the memory, outside React

createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <Dashboard />
  </QueryClientProvider>
);
